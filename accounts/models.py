from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    discord_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    avatar_url = models.URLField(max_length=500, null=True, blank=True)
    is_main_admin = models.BooleanField(default=False)
    is_bot_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    @property
    def is_super_admin(self):
        return self.is_main_admin or self.is_bot_admin
