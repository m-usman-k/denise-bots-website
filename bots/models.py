from django.db import models

class Bot(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

# Note: The data for specific bots (Donations, Giveaways, etc.) is stored in MongoDB.
# We access it directly via PyMongo in the views using shared_database.py
# This ensures that Django ORM does not conflict with MongoDB while still keeping 
# the Django Admin and Auth systems stable on SQLite.
