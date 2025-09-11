from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

from accounts.models import SettingsModel

User = get_user_model()


@receiver(post_save, sender=User)
def create_settings(sender, instance, created, **kwargs):
    """Create user settings on user creation"""
    if created:
        SettingsModel.objects.create(user=instance)
