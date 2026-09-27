from rest_framework import serializers

from inspections.models import (
    InspectionAnswer,
    SanitationInspection,
)

from .models import CorrectiveAction


class CorrectiveActionSerializer(serializers.ModelSerializer):

    class Meta:
        model = CorrectiveAction

        fields = [
            "id",
            "inspection",
            "question",
            "observation",
            "action_required",
            "assigned_to",
            "due_date",
            "action_taken",
            "status",
            "created_by",
            "created_at",
            "updated_at",
            "completed_at",
        ]

        read_only_fields = [
            "id",
            "status",
            "created_by",
            "created_at",
            "updated_at",
            "completed_at",
        ]

    def validate(self, data):

        inspection = data.get("inspection")
        question = data.get("question")

        # Make sure the question belongs to the inspection template
        if question.section.template_id != inspection.template_id:
            raise serializers.ValidationError(
                {
                    "question": (
                        "This question does not belong "
                        "to the inspection template."
                    )
                }
            )

        # Find the answer for this question
        try:
            answer = InspectionAnswer.objects.get(
                inspection=inspection,
                question=question,
            )
        except InspectionAnswer.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "question": (
                        "This question has not been answered "
                        "in this inspection."
                    )
                }
            )

        # Corrective action should only be created for NO
        if answer.answer != InspectionAnswer.AnswerChoices.NO:
            raise serializers.ValidationError(
                {
                    "question": (
                        "A corrective action can only be created "
                        "for a question answered NO."
                    )
                }
            )

        # Use the inspection answer observation if none is supplied
        if not data.get("observation"):
            data["observation"] = answer.observation

        return data

    def create(self, validated_data):

        return CorrectiveAction.objects.create(
            **validated_data,
            created_by=self.context["request"].user,
        )