import os
import uuid
from PIL import Image
from io import BytesIO
from django.db import models
from django.utils import timezone
from django_cleanup import cleanup
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile

from accounts.constants import UserGender, MAX_AVATAR_SIZE


User = get_user_model()


def avatar_image_upload_to(instance, filename: str) -> str:
    """Generate a unique upload path for avatar images."""
    ext = os.path.splitext(filename)[1].lower()
    new_filename = f"{uuid.uuid4()}{ext}"
    return f"accounts/avatars/{instance.user.id}/{new_filename}"


@cleanup.select
class UserProfile(models.Model):
    """
    Extended user profile with avatar support and validations.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # Profile fields
    bio = models.TextField(blank=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=10, choices=UserGender.choices, default=UserGender.OTHER
    )

    # Avatar
    avatar = models.ImageField(upload_to=avatar_image_upload_to, blank=True, null=True)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        indexes = [models.Index(fields=["user"])]

    def __str__(self) -> str:
        return f"{self.user.username}'s profile"

    # ---------------------------
    # Validation
    # ---------------------------

    def clean(self):
        """Model-level validations."""
        today = timezone.now().date()

        # Validate birthday
        if self.birthday:
            if self.birthday > today:
                raise ValidationError({"birthday": "Birthday cannot be in the future."})
            if self.birthday.year < 1900:
                raise ValidationError({"birthday": "Please provide a valid birthday."})

        # Validate avatar file
        if self.avatar and hasattr(self.avatar, "size"):
            if self.avatar.size > MAX_AVATAR_SIZE:
                raise ValidationError({"avatar": "Avatar file size must be under 2MB."})

            valid_extensions = [".jpg", ".jpeg", ".png", ".webp"]
            ext = os.path.splitext(self.avatar.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError(
                    {
                        "avatar": f"Unsupported file type. Allowed: {', '.join(valid_extensions)}"
                    }
                )

    # ---------------------------
    # Image Processing
    # ---------------------------

    def process_avatar(self):
        """Crop, resize & normalize avatar before saving."""
        if not self.avatar:
            return

        img = Image.open(self.avatar)

        # Convert modes (e.g. P, CMYK → RGB)
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")

        # ---- Step 1: Crop to square (center crop) ----
        width, height = img.size
        min_dim = min(width, height)
        left = (width - min_dim) // 2
        top = (height - min_dim) // 2
        right = left + min_dim
        bottom = top + min_dim
        img = img.crop((left, top, right, bottom))

        # ---- Step 2: Resize to 512x512 ----
        target_size = (512, 512)
        img = img.resize(target_size, Image.Resampling.LANCZOS)

        # ---- Step 3: Preserve format ----
        ext = os.path.splitext(self.avatar.name)[1].lower()
        format_map = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".webp": "WEBP"}
        img_format = format_map.get(ext, "PNG")  # fallback to PNG

        img_io = BytesIO()
        img.save(img_io, format=img_format, quality=90)
        img_io.seek(0)

        # ---- Step 4: Replace file ----
        self.avatar = InMemoryUploadedFile(
            img_io,
            field_name="ImageField",
            name=f"{uuid.uuid4()}{ext}",
            content_type=f"image/{img_format.lower()}",
            size=img_io.getbuffer().nbytes,
            charset=None,
        )

    def save(self, *args, **kwargs):
        # Run validations
        self.clean()

        # Process avatar before saving
        if self.avatar:
            self.process_avatar()

        super().save(*args, **kwargs)
