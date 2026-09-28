from django.db import models

from plants.models import Plant


class TitrationLimit(models.Model):

    class TitrationType(models.TextChoices):
        SANITIZER = "SANITIZER", "Sanitizer"
        CHLORAGEL = "CHLORAGEL", "Chloragel"

    plant = models.ForeignKey(
        Plant,
        on_delete=models.PROTECT,
        related_name="titration_limits",
    )

    titration_type = models.CharField(
        max_length=20,
        choices=TitrationType.choices,
    )

    min_value = models.DecimalField(
        max_digits=10,
        decimal_places=4,
    )

    max_value = models.DecimalField(
        max_digits=10,
        decimal_places=4,
    )

    active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return (
            f"{self.plant.code} - "
            f"{self.titration_type} - "
            f"{self.min_value} to "
            f"{self.max_value}"
        )