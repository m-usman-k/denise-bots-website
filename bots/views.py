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
    
    if bot_name == 'donations':
        db = get_mongo_db()
        col = db["bots_donationcategory"]
        categories = list(col.find())
        return render(request, 'bots/donations_dashboard.html', {'categories': categories})
    
    # Handle other bots...
    return render(request, 'bots/bot_detail.html', {'bot_name': bot_name})
