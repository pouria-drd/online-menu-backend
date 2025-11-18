from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.models import ProfileModel


class ProfileSerializer(serializers.ModelSerializer):
    last_name = serializers.CharField(
        min_length=2,
        max_length=50,
        required=False,
        allow_blank=True,
        error_messages={
            "min_length": "Last name must be at least 2 characters",
            "max_length": "Last name must be at most 50 characters",
        },
    )

    first_name = serializers.CharField(
        min_length=2,
        max_length=50,
        required=False,
        allow_blank=True,
        error_messages={
            "min_length": "First name must be at least 2 characters",
            "max_length": "First name must be at most 50 characters",
        },
    )

    class Meta:
        model = ProfileModel
        fields = [
            "full_name",
            "last_name",
            "first_name",
            "avatar",
        ]
        read_only_fields = ["id", "full_name", "created_at", "updated_at"]
