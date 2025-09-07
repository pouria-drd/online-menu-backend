from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

from accounts.models import UserSettings

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_settings(sender, instance, created, **kwargs):
    if created:
        UserSettings.objects.create(user=instance)
