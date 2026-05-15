from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db import connection
from .models import Bot

def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

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
    
    # Map bot names to their MariaDB tables
    collection_map = {
        'donations': 'bots_donationcategory',
        'giveaway': 'bots_giveaway',
        'reputation': 'bots_reputation',
        'ticket': 'bots_ticket',
        'wintracker': 'bots_win',
    }
    
    table_name = collection_map.get(bot_name)
    if not table_name:
        return render(request, 'bots/bot_detail.html', {'bot_name': bot_name, 'data': []})

    with connection.cursor() as cursor:
        # Fetch data (limited to 50 for performance)
        # Using format string for table name is safe here because it's from our map
        query = f"SELECT * FROM {table_name} LIMIT 50"
        cursor.execute(query)
        data = dictfetchall(cursor)
    
    # Special template for donations
    template_name = 'bots/donations_dashboard.html' if bot_name == 'donations' else 'bots/bot_detail.html'
    
    return render(request, template_name, {
        'bot_name': bot_name,
        'data': data
    })
