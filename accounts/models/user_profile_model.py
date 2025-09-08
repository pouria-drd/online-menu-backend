import os
import uuid
from PIL import Image
from io import BytesIO
from django.db import models
from django.utils import timezone
from django_cleanup import cleanup
from accounts.constants import UserGender
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile

User = get_user_model()


def avatar_image_upload_to(instance, filename):
    """Generate a unique upload path for avatar images."""
    # Get the file extension
    ext = os.path.splitext(filename)[1]

    # Create a new filename (e.g., a UUID)
    new_filename = f"{uuid.uuid4()}{ext}"

    # Use the card to card's username for the folder structure
    return f"accounts/avatars/{instance.user.id}/{new_filename}"


@cleanup.select
class UserProfile(models.Model):
    """
    Extended user profile.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    # Names & Bio
    bio = models.TextField(blank=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    # Gender & Birthday
    birthday = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=10, choices=UserGender.choices, default=UserGender.OTHER
    )
    # Avatar
    avatar = models.ImageField(upload_to=avatar_image_upload_to, blank=True, null=True)
    # Profile completion (computed)
    profile_completion = models.PositiveSmallIntegerField(default=0)
    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        indexes = [
            models.Index(fields=["user"]),
        ]

    def clean(self):
        """Validation & computed fields."""
        # Birthday cannot be in the future
        if self.birthday and self.birthday > timezone.now().date():
            raise ValidationError({"birthday": "Birthday cannot be in the future."})

        # Compute profile completion
        fields = ["first_name", "last_name", "bio", "avatar", "gender", "birthday"]
        filled = sum(bool(getattr(self, f)) for f in fields)
        self.profile_completion = int(filled / len(fields) * 100)

    def save(self, *args, **kwargs):
        # Run clean before saving
        self.clean()

        # Resize avatar
        if self.avatar:
            img = Image.open(self.avatar)
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")
            target_size = (512, 512)
            img.thumbnail(target_size, Image.Resampling.LANCZOS)

            img_io = BytesIO()
            img.save(img_io, format="PNG")
            img_io.seek(0)

            self.avatar = InMemoryUploadedFile(
                img_io,
                "ImageField",
                self.avatar.name,
                "image/png",
                img_io.getbuffer().nbytes,
                None,
            )

        super().save(*args, **kwargs)
