from django.contrib.auth.models import User
from django.db import models


class AuditLog(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="audit_logs",
    )

    action = models.CharField(
        max_length=100,
    )

    object_type = models.CharField(
        max_length=100,
    )

    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
    )

    old_values = models.JSONField(
        null=True,
        blank=True,
    )

    new_values = models.JSONField(
        null=True,
        blank=True,
    )

    reason = models.TextField(
        blank=True,
    )

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.action} - "
            f"{self.object_type} #{self.object_id}"
        )