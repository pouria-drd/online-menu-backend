from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

from accounts.models import ProfileModel

User = get_user_model()


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create user profile on user creation"""
    if created:
        ProfileModel.objects.create(user=instance)
