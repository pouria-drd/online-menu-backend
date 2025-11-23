from rest_framework import serializers
from accounts.models import ProfileModel


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for ProfileModel.
    """

    lastName = serializers.CharField(
        source="last_name",
        required=True,
        min_length=2,
        max_length=30,
        error_messages={
            "required": "Last name is required",
            "min_length": "Last name must be at least 2 characters",
            "max_length": "Last name must be at most 30 characters",
        },
    )
    firstName = serializers.CharField(
        source="first_name",
        required=True,
        min_length=2,
        max_length=30,
        error_messages={
            "required": "First name is required",
            "min_length": "First name must be at least 2 characters",
            "max_length": "First name must be at most 30 characters",
        },
    )

    class Meta:
        model = ProfileModel

        fields = [
            "avatar",
            "lastName",
            "firstName",
        ]

        read_only_fields = [
            "id",
            "user",
            "updated_at",
            "created_at",
        ]
