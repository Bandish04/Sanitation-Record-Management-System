from django.contrib.auth.models import User
from django.db import models

from plants.models import Plant


class InspectionTemplate(models.Model):

    name = models.CharField(max_length=200)

    description = models.TextField(
        blank=True
    )

    active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name


class InspectionSection(models.Model):

    template = models.ForeignKey(
        InspectionTemplate,
        on_delete=models.CASCADE,
        related_name="sections",
    )

    name = models.CharField(
        max_length=200
    )

    order = models.PositiveIntegerField(
        default=1
    )

    def __str__(self):
        return f"{self.template.name} - {self.name}"


class InspectionQuestion(models.Model):

    section = models.ForeignKey(
        InspectionSection,
        on_delete=models.CASCADE,
        related_name="questions",
    )

    question_text = models.CharField(
        max_length=500
    )

    order = models.PositiveIntegerField(
        default=1
    )

    requires_observation_on_no = models.BooleanField(
        default=False
    )

    active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.question_text

class SanitationInspection(models.Model):

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
        CORRECTED = "CORRECTED", "Corrected"
        REVIEW_REQUIRED = "REVIEW_REQUIRED", "Review Required"

    plant = models.ForeignKey(
        Plant,
        on_delete=models.PROTECT,
        related_name="sanitation_inspections",
    )

    template = models.ForeignKey(
        InspectionTemplate,
        on_delete=models.PROTECT,
        related_name="inspections",
    )

    inspection_date = models.DateField()

    inspector = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="sanitation_inspections",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    general_notes = models.TextField(
        blank=True
    )

    signed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return (
            f"{self.plant.code} - "
            f"{self.inspection_date} - "
            f"{self.inspector.username}"
        )


class InspectionAnswer(models.Model):

    class AnswerChoices(models.TextChoices):
        YES = "YES", "Yes"
        NO = "NO", "No"
        NA = "NA", "N/A"

    inspection = models.ForeignKey(
        SanitationInspection,
        on_delete=models.CASCADE,
        related_name="answers",
    )

    question = models.ForeignKey(
        InspectionQuestion,
        on_delete=models.PROTECT,
        related_name="answers",
    )

    answer = models.CharField(
        max_length=3,
        choices=AnswerChoices.choices,
    )

    observation = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return (
            f"{self.inspection} - "
            f"{self.question.question_text}"
        )