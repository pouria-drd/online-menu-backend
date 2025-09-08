from rest_framework import serializers
from accounts.models import UserModel
from .user_profile_serializer import UserProfileSerializer
from .user_settings_serializer import UserSettingsSerializer


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    settings = UserSettingsSerializer(read_only=True)

    primaryEmail = serializers.SerializerMethodField()
    primaryPhoneNumber = serializers.SerializerMethodField()
    emailVerified = serializers.SerializerMethodField()
    phoneVerified = serializers.SerializerMethodField()

    cratedAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = UserModel
        fields = [
            "id",
            "username",
            "primaryEmail",
            "primaryPhoneNumber",
            "emailVerified",
            "phoneVerified",
            "role",
            "updatedAt",
            "cratedAt",
            "profile",
            "settings",
        ]
        read_only_fields = [
            "id",
            "status",
            "role",
            "is_staff",
            "cratedAt",
            "updatedAt",
            "deleted_at",
            "profile",
            "settings",
        ]

    def get_primaryEmail(self, obj):
        """Get primary email from prefetched data"""
        # Use cached prefetched data
        if hasattr(obj, "primary_emails"):
            return obj.primary_emails[0].email if obj.primary_emails else None

        # Fallback to regular prefetched emails
        primary_emails = [e for e in obj.emails.all() if e.is_primary]
        return primary_emails[0].email if primary_emails else None

    def get_primaryPhoneNumber(self, obj):
        """Get primary phone from prefetched data"""
        # Use cached prefetched data
        if hasattr(obj, "primary_phones"):
            return obj.primary_phones[0].phone_number if obj.primary_phones else None

        # Fallback to regular prefetched phones
        primary_phones = [p for p in obj.phones.all() if p.is_primary]
        return primary_phones[0].phone_number if primary_phones else None

    def get_emailVerified(self, obj):
        """Check if email is verified from prefetched data"""
        if hasattr(obj, "primary_emails"):
            return obj.primary_emails[0].is_verified if obj.primary_emails else False

        primary_emails = [e for e in obj.emails.all() if e.is_primary]
        return primary_emails[0].is_verified if primary_emails else False

    def get_phoneVerified(self, obj):
        """Check if phone is verified from prefetched data"""
        if hasattr(obj, "primary_phones"):
            return obj.primary_phones[0].is_verified if obj.primary_phones else False

        primary_phones = [p for p in obj.phones.all() if p.is_primary]
        return primary_phones[0].is_verified if primary_phones else False
