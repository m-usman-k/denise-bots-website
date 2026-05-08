from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Bot, DonationCategory, UserDonation, DonationSettings

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
        categories = DonationCategory.objects.all()
        # For simplicity, we'll just show the donation dashboard
        return render(request, 'bots/donations_dashboard.html', {'categories': categories})
    
    # Handle other bots...
    return render(request, 'bots/bot_detail.html', {'bot_name': bot_name})
