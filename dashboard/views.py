from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import CustomUser
from bots.models import Bot
from django.contrib.auth import get_user_model

User = get_user_model()

def home(request):
    return render(request, 'dashboard/home.html')

@login_required
def dashboard(request):
    # Only super admins can access the dashboard for now
    if not request.user.is_super_admin:
        messages.error(request, "Access denied. Only super admins can view the dashboard.")
        return redirect('home')
    
    bots = Bot.objects.all()
    user_count = User.objects.count()
    active_bots = Bot.objects.filter(is_active=True).count()
    
    context = {
        'bots': bots,
        'user_count': user_count,
        'active_bots': active_bots,
    }
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def manage_admins(request):
    # Only main admin (simpleprog) can manage other admins
    if not request.user.is_main_admin:
        messages.error(request, "Access denied. Only the main super admin can manage other admins.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        
        if action == 'add':
            username = request.POST.get('username')
            try:
                user_to_promote = User.objects.get(username=username)
                user_to_promote.is_bot_admin = True
                user_to_promote.save()
                messages.success(request, f"{username} is now a super admin (limited).")
            except User.DoesNotExist:
                messages.error(request, f"User {username} not found.")
        
        elif action == 'remove':
            user_to_demote = get_object_or_404(User, id=user_id)
            if user_to_demote.username == 'simpleprog':
                messages.error(request, "You cannot demote the main admin.")
            else:
                user_to_demote.is_bot_admin = False
                user_to_demote.save()
                messages.success(request, f"{user_to_demote.username} is no longer a super admin.")
        
        return redirect('manage_admins')

    admins = User.objects.filter(is_bot_admin=True) | User.objects.filter(is_main_admin=True)
    return render(request, 'dashboard/manage_admins.html', {'admins': admins})
