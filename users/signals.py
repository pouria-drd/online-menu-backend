from django.db import transaction
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

from users.models import ProfileModel, SettingsModel

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_related_models(sender, instance, created, **kwargs):
    """
    Create ProfileModel and SettingsModel for new users automatically.

    Wrapped in a transaction to ensure atomicity.
    """
    if not created:
        return

    try:
        with transaction.atomic():
            ProfileModel.objects.create(user=instance)
            SettingsModel.objects.create(user=instance)
    except Exception as e:
        import logging

        logger = logging.getLogger("users.signals")
        logger.error(f"Failed to create user related models: {e}")
        raise
