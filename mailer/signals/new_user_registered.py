from django.dispatch import receiver
from accounts.models import UserModel
from django.db.models.signals import post_save
from mailer.utils import send_admin_new_user_alert_task


@receiver(post_save, sender=UserModel)
def new_user_registered(sender, instance, created, **kwargs):
    """Trigger admin alert when a new user registers."""
    if created:  # only run for new user, not updates
        send_admin_new_user_alert_task(instance, use_template=False)
