from rest_framework import serializers
from users.models import SettingsModel


class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SettingsModel
        fields = ["theme", "language"]
        read_only_fields = ["id", "created_at", "updated_at"]
