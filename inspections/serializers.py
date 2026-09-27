from rest_framework import serializers

from .models import (
    InspectionTemplate,
    InspectionSection,
    InspectionQuestion,
)


class InspectionQuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = InspectionQuestion

        fields = [
            "id",
            "section",
            "question_text",
            "order",
            "requires_observation_on_no",
            "active",
        ]

        read_only_fields = [
            "id",
        ]


class InspectionSectionSerializer(serializers.ModelSerializer):

    questions = InspectionQuestionSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = InspectionSection

        fields = [
            "id",
            "template",
            "name",
            "order",
            "questions",
        ]

        read_only_fields = [
            "id",
            "questions",
        ]


class InspectionTemplateSerializer(serializers.ModelSerializer):

    sections = InspectionSectionSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = InspectionTemplate

        fields = [
            "id",
            "name",
            "description",
            "active",
            "sections",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "sections",
            "created_at",
            "updated_at",
        ]