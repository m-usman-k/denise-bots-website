from django.db import models

class Bot(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

# Donation Bot Models
class DonationCategory(models.Model):
    guild_id = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    class Meta:
        unique_together = ('guild_id', 'name')

class UserDonation(models.Model):
    guild_id = models.CharField(max_length=100)
    user_id = models.CharField(max_length=100)
    category = models.ForeignKey(DonationCategory, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
    class Meta:
        unique_together = ('guild_id', 'user_id', 'category')

class DonationSettings(models.Model):
    guild_id = models.CharField(max_length=100, unique=True)
    log_channel_id = models.CharField(max_length=100, null=True, blank=True)

class DonationManager(models.Model):
    guild_id = models.CharField(max_length=100)
    role_id = models.CharField(max_length=100)

class DonationAutorole(models.Model):
    guild_id = models.CharField(max_length=100)
    category = models.ForeignKey(DonationCategory, on_delete=models.CASCADE)
    threshold = models.IntegerField()
    role_id = models.CharField(max_length=100)

# Giveaway Bot Models
class Giveaway(models.Model):
    message_id = models.CharField(max_length=100, primary_key=True)
    guild_id = models.CharField(max_length=100)
    channel_id = models.CharField(max_length=100)
    required_role_id = models.CharField(max_length=100, null=True, blank=True)
    host_user_id = models.CharField(max_length=100)
    prize = models.CharField(max_length=255)
    winners_count = models.IntegerField(default=1)
    end_time = models.IntegerField()
    processed = models.BooleanField(default=False)

class GiveawayEntry(models.Model):
    giveaway = models.ForeignKey(Giveaway, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=100)
    class Meta:
        unique_together = ('giveaway', 'user_id')

class GiveawayRoleBonus(models.Model):
    guild_id = models.CharField(max_length=100)
    role_id = models.CharField(max_length=100)
    entries = models.IntegerField(default=1)
    class Meta:
        unique_together = ('guild_id', 'role_id')

# Reputation Bot Models
class UserReputation(models.Model):
    guild_id = models.CharField(max_length=100)
    user_id = models.CharField(max_length=100)
    points = models.IntegerField(default=0)
    class Meta:
        unique_together = ('guild_id', 'user_id')

# Ticket Bot Models
class Ticket(models.Model):
    guild_id = models.CharField(max_length=100)
    user_id = models.CharField(max_length=100)
    channel_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

# Win Tracker Models
class UserWin(models.Model):
    guild_id = models.CharField(max_length=100)
    user_id = models.CharField(max_length=100)
    wins = models.IntegerField(default=0)
    class Meta:
        unique_together = ('guild_id', 'user_id')
