from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import os
from .models import Bot
from pymongo import MongoClient

def get_mongo_db():
    uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
    db_name = os.environ.get('MONGO_DB_NAME', 'denise_bots')
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
