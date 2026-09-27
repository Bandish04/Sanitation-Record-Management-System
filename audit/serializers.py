from rest_framework import serializers

from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    class Meta:
        model = AuditLog

        fields = [
            "id",
            "user",
            "username",
            "action",
            "object_type",
            "object_id",
            "timestamp",
            "old_values",
            "new_values",
            "reason",
        ]

        read_only_fields = [
            "id",
            "user",
            "username",
            "action",
            "object_type",
            "object_id",
            "timestamp",
            "old_values",
            "new_values",
            "reason",
        ]