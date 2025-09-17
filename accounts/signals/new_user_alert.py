from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

from accounts.utils import send_new_user_alert


User = get_user_model()


@receiver(post_save, sender=User)
def new_user_alert(sender, instance, created, **kwargs):
    """Trigger admin alert when a new user registers."""
    if created:  # only run for new user, not updates
        send_new_user_alert(instance)
