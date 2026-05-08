from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings

class DiscordAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        
        # Extract discord data
        data = sociallogin.account.extra_data
        user.discord_id = data.get('id')
        user.avatar_url = f"https://cdn.discordapp.com/avatars/{user.discord_id}/{data.get('avatar')}.png"
        
        # Check if this is the main admin
        if user.username == 'simpleprog':
            user.is_main_admin = True
            user.is_staff = True
            user.is_superuser = True
            
        user.save()
        return user
