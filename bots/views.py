from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Bot
from pymongo import MongoClient

def get_mongo_db():
    db_config = settings.DATABASES['default']
    
    # Build the URI from the structured settings
    user = db_config.get('USER')
    password = db_config.get('PASSWORD')
    host = db_config.get('HOST', 'localhost')
    port = db_config.get('PORT', 27017)
    db_name = db_config.get('NAME', 'denise_bots')
    auth_source = db_config.get('CLIENT', {}).get('authSource', 'admin')
    
    if user and password:
        uri = f"mongodb://{user}:{password}@{host}:{port}/?authSource={auth_source}"
    else:
        uri = f"mongodb://{host}:{port}/"
        
    client = MongoClient(uri)
    return client[db_name]

@login_required
def bot_list(request):
    if not request.user.is_super_admin:
        return redirect('home')
    bots = Bot.objects.all()
    return render(request, 'bots/bot_list.html', {'bots': bots})

@login_required
def bot_detail(request, bot_name):
    if not request.user.is_super_admin:
        return redirect('home')
    
    # Map bot names to their MongoDB collections
    collection_map = {
        'donations': 'bots_donationcategory',
        'giveaway': 'bots_giveaway',
        'reputation': 'bots_reputation',
        'ticket': 'bots_ticket',
        'wintracker': 'bots_win',
    }
    
    col_name = collection_map.get(bot_name)
    if not col_name:
        return render(request, 'bots/bot_detail.html', {'bot_name': bot_name, 'data': []})

    db = get_mongo_db()
    col = db[col_name]
    
    # Fetch data (limited to 50 for performance)
    data = list(col.find().limit(50))
    
    # Special template for donations if you want to keep it, 
    # otherwise we use the unified bot_detail.html
    template_name = 'bots/donations_dashboard.html' if bot_name == 'donations' else 'bots/bot_detail.html'
    
    return render(request, template_name, {
        'bot_name': bot_name,
        'data': data
    })
