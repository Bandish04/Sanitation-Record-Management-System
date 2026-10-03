from rest_framework import serializers

from inspections.models import InspectionAnswer

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
            "created_by",
            "created_at",
            "updated_at",
            "completed_at",
        ]
        extra_kwargs = {
            "observation": {
           "required": False,
            "allow_blank": True,
        },
}

    def validate_status(self, value):

        instance = self.instance

        # Status validation is only needed when updating
        if instance is None:
            return value

        current_status = instance.status

        allowed_transitions = {
            CorrectiveAction.Status.OPEN: [
                CorrectiveAction.Status.IN_PROGRESS,
                CorrectiveAction.Status.CANCELLED,
            ],

            CorrectiveAction.Status.IN_PROGRESS: [
                CorrectiveAction.Status.COMPLETED,
                CorrectiveAction.Status.CANCELLED,
            ],
        }

        if current_status == value:
            return value

        if value not in allowed_transitions.get(
            current_status,
            [],
        ):
            raise serializers.ValidationError(
                f"Cannot change status from "
                f"{current_status} to {value}."
            )

        return value

    def validate(self, data):

        # For PATCH, use existing values when fields
        # are not included in request.data.
        inspection = data.get(
            "inspection",
            self.instance.inspection if self.instance else None,
        )

        question = data.get(
            "question",
            self.instance.question if self.instance else None,
        )

        # These are required when creating a new action.
        if inspection is None:
            raise serializers.ValidationError(
                {
                    "inspection": "This field is required."
                }
            )

        if question is None:
            raise serializers.ValidationError(
                {
                    "question": "This field is required."
                }
            )

        # Make sure the question belongs to the
        # inspection template.
        if question.section.template_id != inspection.template_id:
            raise serializers.ValidationError(
                {
                    "question": (
                        "This question does not belong "
                        "to the inspection template."
                    )
                }
            )

        # Check the answer for this question.
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

        # Corrective actions must be associated
        # with a NO answer.
        if answer.answer != InspectionAnswer.AnswerChoices.NO:
            raise serializers.ValidationError(
                {
                    "question": (
                        "A corrective action can only be created "
                        "for a question answered NO."
                    )
                }
            )

        # Only automatically copy the observation
        # when creating a new corrective action.
        if self.instance is None:
            if not data.get("observation"):
                data["observation"] = answer.observation

        return data

    def create(self, validated_data):

        return CorrectiveAction.objects.create(
            **validated_data,
            created_by=self.context["request"].user,
        )