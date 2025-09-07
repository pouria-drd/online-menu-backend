from rest_framework import serializers
from accounts.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    lastName = serializers.CharField(source="last_name")
    firstName = serializers.CharField(source="first_name")

    profileCompletion = serializers.SerializerMethodField(
        source="profile_completion", read_only=True
    )

    updatedAt = serializers.DateTimeField(read_only=True)
    createdAt = serializers.DateTimeField(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "bio",
            "gender",
            "birthday",
            "lastName",
            "firstName",
            "avatar",
            "profileCompletion",
            "updatedAt",
            "createdAt",
        ]
        read_only_fields = [
            "id",
            "user",
            "updatedAt",
            "createdAt",
            "profileCompletion",
        ]

    def get_profileCompletion(self, obj):
        return f"{obj.profile_completion}%"

    def update(self, instance, validated_data):
        # Allow partial updates for nested fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
