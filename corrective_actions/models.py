from django.contrib.auth.models import User
from django.db import models

from inspections.models import (
    SanitationInspection,
    InspectionQuestion,
)


class CorrectiveAction(models.Model):

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    inspection = models.ForeignKey(
        SanitationInspection,
        on_delete=models.PROTECT,
        related_name="corrective_actions",
    )

    question = models.ForeignKey(
        InspectionQuestion,
        on_delete=models.PROTECT,
        related_name="corrective_actions",
    )

    observation = models.TextField()

    action_required = models.TextField()

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="assigned_corrective_actions",
        null=True,
        blank=True,
    )

    due_date = models.DateField(
        null=True,
        blank=True,
    )

    action_taken = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_corrective_actions",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return (
            f"Corrective Action #{self.id} - "
            f"{self.status}"
        )