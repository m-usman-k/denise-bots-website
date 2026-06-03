from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.db import connection
from .models import Bot
import subprocess
import json
import time

@login_required
def set_guild(request):
    if not request.user.is_super_admin:
        return redirect('home')
    if request.method == 'POST':
        guild_id_str = request.POST.get('guild_id')
        if guild_id_str and guild_id_str.isdigit():
            request.session['active_guild_id'] = int(guild_id_str)
            messages.success(request, f"Active Discord Server set to: {guild_id_str}")
        else:
            messages.error(request, "Invalid Guild ID.")
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def get_pm2_status():
    try:
        # Run pm2 jlist and parse JSON output
        result = subprocess.run(['pm2', 'jlist'], capture_output=True, text=True)
        if result.returncode == 0:
            pm2_data = json.loads(result.stdout)
            status_dict = {}
            for process in pm2_data:
                name = process.get('name')
                pm2_env = process.get('pm2_env', {})
                status = pm2_env.get('status', 'offline')
                uptime = pm2_env.get('pm_uptime', 0)
                
                # Format uptime nicely
                uptime_str = "0s"
                if uptime > 0:
                    diff = int(time.time() * 1000) - uptime
                    seconds = diff // 1000
                    minutes = seconds // 60
                    hours = minutes // 60
                    if hours > 0: uptime_str = f"{hours}h {minutes % 60}m"
                    elif minutes > 0: uptime_str = f"{minutes}m"
                    else: uptime_str = f"{seconds}s"

                monit = process.get('monit', {})
                cpu = monit.get('cpu', 0)
                memory = monit.get('memory', 0)
                memory_mb = round(memory / (1024 * 1024), 1)

                status_dict[name] = {
                    'status': status,
                    'uptime': uptime_str,
                    'cpu': cpu,
                    'memory': memory_mb
                }
            return status_dict
    except Exception as e:
        print(f"Error fetching PM2 status: {e}")
    return {}

@login_required
def bot_list(request):
    if not request.user.is_super_admin:
        return redirect('home')
    
    bots = Bot.objects.all()
    pm2_status = get_pm2_status()
    
    # Map model instances to their pm2 process name
    # assuming db bots are named like 'Ticket Bot' -> pm2 'ticketbot' etc.
    # or we just match the actual pm2 names explicitly:
    pm2_name_map = {
        'Donations': 'donationbot',
        'Giveaway': 'giveawaybot',
        'Reputation': 'reputationbot',
        'Ticket': 'ticketbot',
        'WinTracker': 'wintrackerbot',
    }

    bot_data = []
    for bot in bots:
        # Fallback to lowercase without spaces if not in map
        pm2_name = pm2_name_map.get(bot.name, bot.name.lower().replace(' ', '') + 'bot')
        
        info = pm2_status.get(pm2_name, {'status': 'offline', 'uptime': '0s', 'cpu': 0, 'memory': 0})
        
        bot_data.append({
            'bot': bot,
            'pm2_name': pm2_name,
            'status': info['status'],
            'uptime': info['uptime'],
            'cpu': info['cpu'],
            'memory': info['memory']
        })

    return render(request, 'bots/bot_list.html', {'bot_data': bot_data})

@login_required
def manage_bot(request):
    if not request.user.is_super_admin:
        messages.error(request, "Access denied.")
        return redirect('home')
        
    if request.method == 'POST':
        action = request.POST.get('action')
        pm2_name = request.POST.get('pm2_name')
        
        if action in ['start', 'stop', 'restart'] and pm2_name:
            try:
                subprocess.run(['pm2', action, pm2_name], check=True)
                messages.success(request, f"Successfully executed '{action}' on {pm2_name}.")
            except subprocess.CalledProcessError:
                messages.error(request, f"Failed to {action} {pm2_name}. Please check the server logs.")
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
                
    return redirect('bot_list')

from .db_client import SharedDatabase

@login_required
def bot_detail(request, bot_name):
    if not request.user.is_super_admin:
        return redirect('home')
        
    db = SharedDatabase()
    
    guild_id = request.session.get('active_guild_id')
    if not guild_id:
        # Since these bots are private, auto-fetch the single guild_id from DB
        conn = db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT guild_id FROM don_settings LIMIT 1")
            result = cursor.fetchone()
        finally:
            conn.close()
            
        if result:
            guild_id = result[0]
            request.session['active_guild_id'] = guild_id
        else:
            # Fallback if DB is completely empty
            guild_id = 1487090828190154997 # Extracted from the VariableDoesNotExist log earlier
            request.session['active_guild_id'] = guild_id
    
    if bot_name == 'donations':
        return render_donations_dashboard(request, db, guild_id)
    elif bot_name == 'giveaway':
        return render_giveaways_dashboard(request, db)
    elif bot_name == 'reputation':
        return render_reputation_dashboard(request, db, guild_id)
    elif bot_name == 'ticket':
        return render_ticket_dashboard(request, db, guild_id)
    elif bot_name == 'wintracker':
        return render_wintracker_dashboard(request, db)
    else:
        return redirect('dashboard')

def render_donations_dashboard(request, db, guild_id):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_manager':
            role_id = request.POST.get('role_id')
            if role_id and role_id.isdigit():
                db.add_manager(guild_id, int(role_id))
                messages.success(request, "Manager role added.")
                
        elif action == 'remove_manager':
            role_id = request.POST.get('role_id')
            if role_id:
                db.remove_manager(guild_id, int(role_id))
                messages.success(request, "Manager role removed.")
                
        elif action == 'create_category':
            name = request.POST.get('name')
            if name:
                db.create_donation_category(guild_id, name)
                messages.success(request, f"Category '{name}' created.")
                
        elif action == 'delete_category':
            name = request.POST.get('name')
            if name:
                db.delete_donation_category(guild_id, name)
                messages.success(request, f"Category '{name}' deleted.")
                
        elif action == 'update_settings':
            log_channel = request.POST.get('log_channel_id')
            if log_channel and log_channel.isdigit():
                db.set_don_logs(guild_id, int(log_channel))
                messages.success(request, "Log channel updated.")
                
        elif action == 'add_autorole':
            category = request.POST.get('category')
            role_id = request.POST.get('role_id')
            threshold = request.POST.get('threshold')
            if category and role_id and threshold:
                db.add_autorole(guild_id, category, int(role_id), int(threshold))
                messages.success(request, "Auto-role added.")
                
        elif action == 'remove_autorole':
            category = request.POST.get('category')
            role_id = request.POST.get('role_id')
            threshold = request.POST.get('threshold')
            if category and role_id and threshold:
                db.remove_autorole(guild_id, category, int(role_id), int(threshold))
                messages.success(request, "Auto-role removed.")
                
        elif action == 'edit_user_donation':
            user_id = request.POST.get('user_id')
            category = request.POST.get('category')
            amount = request.POST.get('amount')
            if user_id and category and amount:
                db.update_user_donation(guild_id, int(user_id), category, int(amount))
                messages.success(request, "User donation updated.")
                
        return redirect('bot_detail', bot_name='donations')

    # Fetch data
    categories = [row[0] for row in db.get_donation_categories(guild_id)]
    managers = db.get_managers(guild_id)
    settings = db.get_guild_settings(guild_id)
    all_autoroles = db.get_all_autoroles(guild_id)
    
    # Donors per category
    donors = {}
    for cat in categories:
        donors[cat] = db.get_donation_leaderboard(guild_id, cat)

    context = {
        'bot_name': 'donations',
        'guild_id': guild_id,
        'categories': categories,
        'managers': managers,
        'settings': settings,
        'autoroles': all_autoroles,
        'donors': donors
    }
    return render(request, 'bots/donations_dashboard.html', context)

def render_giveaways_dashboard(request, db):
    return render(request, 'bots/giveaway_dashboard.html', {})
def render_reputation_dashboard(request, db, guild_id):
    return render(request, 'bots/reputation_dashboard.html', {})
def render_ticket_dashboard(request, db, guild_id):
    return render(request, 'bots/ticket_dashboard.html', {})
def render_wintracker_dashboard(request, db):
    return render(request, 'bots/wintracker_dashboard.html', {})

@login_required
def bot_logs(request, pm2_name):
    if not request.user.is_super_admin:
        messages.error(request, "Access denied.")
        return redirect('home')

    logs_content = ""
    try:
        # Run pm2 logs --nostream --lines 100
        result = subprocess.run(
            ['pm2', 'logs', pm2_name, '--nostream', '--lines', '100'],
            capture_output=True,
            text=True
        )
        logs_content = result.stdout
        
        # If stdout is empty, it might be in stderr depending on pm2 version
        if not logs_content.strip():
            logs_content = result.stderr
            
        # Clean up ANSI color codes if any
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        logs_content = ansi_escape.sub('', logs_content)
        
    except Exception as e:
        logs_content = f"Error fetching logs: {e}"

    return render(request, 'bots/bot_logs.html', {
        'pm2_name': pm2_name,
        'logs_content': logs_content
    })

import os
from django.http import JsonResponse
from pathlib import Path

# Map database bot names to actual directory names on VPS
BOT_DIR_MAP = {
    'donations': 'Donations Bot',
    'giveaway': 'Giveaway Bot',
    'reputation': 'Reputation Bot',
    'ticket': 'Ticket Bot',
    'wintracker': 'Win Tracker',
}

BASE_BOTS_PATH = "/home/ubuntu/denise-bots"

def get_bot_abs_path(bot_name):
    bot_dir_name = BOT_DIR_MAP.get(bot_name.lower())
    if not bot_dir_name:
        bot_dir_name = bot_name
    return os.path.abspath(os.path.join(BASE_BOTS_PATH, bot_dir_name))

def is_safe_path(base_dir, requested_path):
    base = os.path.abspath(base_dir)
    target = os.path.abspath(requested_path)
    return target.startswith(base)

@login_required
def bot_editor(request, bot_name):
    if not request.user.is_super_admin:
        return redirect('home')
    
    bot_dir = get_bot_abs_path(bot_name)
    if not os.path.exists(bot_dir):
        messages.error(request, f"Bot directory not found for {bot_name}")
        return redirect('bot_list')
        
    return render(request, 'bots/bot_editor.html', {
        'bot_name': bot_name,
        'bot_dir_name': BOT_DIR_MAP.get(bot_name.lower(), bot_name)
    })

@login_required
def api_fs_list(request):
    if not request.user.is_super_admin:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    bot_name = request.GET.get('bot_name')
    sub_path = request.GET.get('path', '')
    
    base_dir = get_bot_abs_path(bot_name)
    target_dir = os.path.abspath(os.path.join(base_dir, sub_path))
    
    if not is_safe_path(base_dir, target_dir):
        return JsonResponse({'error': 'Path traversal blocked'}, status=403)
        
    if not os.path.exists(target_dir):
        return JsonResponse({'error': 'Directory not found'}, status=404)
        
    items = []
    try:
        for entry in os.scandir(target_dir):
            if entry.name in ['__pycache__', 'venv', '.git', '.env']:
                continue
            items.append({
                'name': entry.name,
                'path': os.path.relpath(entry.path, base_dir).replace('\\', '/'),
                'is_dir': entry.is_dir(),
                'size': entry.stat().st_size if entry.is_file() else 0
            })
        items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
        return JsonResponse({'items': items})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def api_fs_read(request):
    if not request.user.is_super_admin:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    bot_name = request.GET.get('bot_name')
    file_path = request.GET.get('path', '')
    
    base_dir = get_bot_abs_path(bot_name)
    target_file = os.path.abspath(os.path.join(base_dir, file_path))
    
    if not is_safe_path(base_dir, target_file) or not os.path.isfile(target_file):
        return JsonResponse({'error': 'File not found or blocked'}, status=404)
        
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return JsonResponse({'content': content})
    except UnicodeDecodeError:
        return JsonResponse({'error': 'Binary files cannot be read'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def api_fs_write(request):
    if not request.user.is_super_admin:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    if request.method != 'POST':
        return JsonResponse({'error': 'Must be POST'}, status=405)
        
    try:
        data = json.loads(request.body)
        bot_name = data.get('bot_name')
        file_path = data.get('path', '')
        content = data.get('content', '')
        
        base_dir = get_bot_abs_path(bot_name)
        target_file = os.path.abspath(os.path.join(base_dir, file_path))
        
        if not is_safe_path(base_dir, target_file):
            return JsonResponse({'error': 'Path traversal blocked'}, status=403)
            
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
