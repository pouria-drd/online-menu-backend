import os
import uuid
from PIL import Image

from django.db import models
from django_cleanup import cleanup
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from core.constants import (
    MAX_AVATAR_SIZE,
    MAX_AVATAR_SIZE_MB,
    VALID_AVATAR_EXTENSIONS,
)


UserModel = get_user_model()


def avatar_image_upload_to(instance, filename: str) -> str:
    """Generate a unique upload path for avatar images."""
    # Get the file extension
    ext = os.path.splitext(filename)[1]

    # Create a new filename (e.g., a UUID)
    new_filename = f"{uuid.uuid4()}{ext}"

    # Use the project's name for the folder structure
    return f"accounts/avatars/{instance.user.id}/{new_filename}"


@cleanup.select
class ProfileModel(models.Model):
    """Extended user profile with avatar support and validations."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        UserModel, on_delete=models.CASCADE, related_name="profile", db_index=True
    )

    avatar = models.ImageField(upload_to=avatar_image_upload_to, blank=True, null=True)

    last_name = models.CharField(max_length=50, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self) -> str:
        return f"{self.full_name or self.user.email}'s profile"

    @property
    def full_name(self) -> str:
        """Return the user's full name."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        if not full_name:
            return self.user.email
        return full_name

    def clean(self):
        if self.avatar:
            ext = os.path.splitext(self.avatar.name)[1].lower()
            if ext not in VALID_AVATAR_EXTENSIONS:
                raise ValidationError({"avatar": f"Unsupported file type: {ext}"})
            if self.avatar.size > MAX_AVATAR_SIZE:
                raise ValidationError(
                    {"avatar": f"Avatar must be under {MAX_AVATAR_SIZE_MB}MB"}
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


@receiver(models.signals.post_save, sender=ProfileModel)
def resize_image(sender, instance, **kwargs):
    """Resize the avatar image if it's larger than 512x512 pixels."""
    if instance.avatar:
        img = Image.open(instance.avatar.path)
        if img.width > 512 or img.height > 512:
            img.thumbnail((512, 512))
            img.save(instance.avatar.path)
