from django.contrib.auth.models import User
from django.db import models

from plants.models import Plant


class SanitizerTitration(models.Model):

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
        CORRECTED = "CORRECTED", "Corrected"
        REVIEW_REQUIRED = "REVIEW_REQUIRED", "Review Required"

    plant = models.ForeignKey(
        Plant,
        on_delete=models.PROTECT,
        related_name="sanitizer_titrations",
    )

    sample_volume_ml = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=5.00,
        editable=False,
    )

    r71_drops = models.PositiveIntegerField()

    ppm = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        editable=False,
    )

    percent_vv = models.DecimalField(
        max_digits=6,
        decimal_places=4,
        editable=False,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_sanitizer_titrations",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return (
            f"{self.plant.code} - "
            f"{self.r71_drops} drops - "
            f"{self.ppm} ppm"
        )

class ChloragelTitration(models.Model):

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
        CORRECTED = "CORRECTED", "Corrected"
        REVIEW_REQUIRED = "REVIEW_REQUIRED", "Review Required"

    plant = models.ForeignKey(
        Plant,
        on_delete=models.PROTECT,
        related_name="chloragel_titrations",
    )

    sample_volume_ml = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=15.00,
        editable=False,
    )

    r9_drops = models.PositiveIntegerField()

    result_percent = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        editable=False,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_chloragel_titrations",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return (
            f"{self.plant.code} - "
            f"{self.r9_drops} drops - "
            f"{self.result_percent}%"
        )