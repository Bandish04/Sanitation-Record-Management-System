
from rest_framework import serializers

from inspections.models import InspectionAnswer

from .models import CorrectiveAction


class CorrectiveActionSerializer(serializers.ModelSerializer):
    inspection_display = serializers.SerializerMethodField()

    plant_name = serializers.CharField(
        source="inspection.plant.name",
        read_only=True,
    )
    plant_code = serializers.CharField(
        source="inspection.plant.code",
        read_only=True,
    )
    inspection_date = serializers.DateField(
        source="inspection.inspection_date",
        read_only=True,
    )
    template_name = serializers.CharField(
        source="inspection.template.name",
        read_only=True,
    )
    question_text = serializers.SerializerMethodField()
    is_custom_question = serializers.SerializerMethodField()

    assigned_to_username = serializers.CharField(
        source="assigned_to.username",
        read_only=True,
        allow_null=True,
    )
    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )

    class Meta:
        model = CorrectiveAction
        fields = [
            "id",
            "inspection",
            "inspection_display",
            "plant_name",
            "plant_code",
            "inspection_date",
            "template_name",
            "question",
            "question_text",
            "is_custom_question",
            "observation",
            "action_required",
            "assigned_to",
            "assigned_to_username",
            "due_date",
            "action_taken",
            "status",
            "created_by",
            "created_by_username",
            "created_at",
            "updated_at",
            "completed_at",
        ]
        read_only_fields = [
            "id",
            "inspection_display",
            "plant_name",
            "plant_code",
            "inspection_date",
            "template_name",
            "question_text",
            "is_custom_question",
            "assigned_to_username",
            "created_by",
            "created_by_username",
            "created_at",
            "updated_at",
            "completed_at",
        ]
        extra_kwargs = {
            "question": {
                "required": False,
                "allow_null": True,
            },
            "observation": {
                "required": False,
                "allow_blank": True,
            },
        }

    def get_inspection_display(self, obj):
        if not obj.inspection:
            return ""

        parts = []
        if obj.inspection.plant:
            parts.append(obj.inspection.plant.name)
        if obj.inspection.template:
            parts.append(obj.inspection.template.name)
        if obj.inspection.inspection_date:
            parts.append(str(obj.inspection.inspection_date))

        return " - ".join(parts)

    def get_question_text(self, obj):
        if obj.question_id:
            return obj.question.question_text
        return "N/A — Custom Question"

    def get_is_custom_question(self, obj):
        return obj.question_id is None

    def validate_status(self, value):
        instance = self.instance
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

        if value not in allowed_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"Cannot change status from {current_status} to {value}."
            )

        return value

    def validate(self, data):
        instance = self.instance

        inspection = data.get(
            "inspection",
            instance.inspection if instance else None,
        )

        if "question" in data:
            question = data["question"]
        else:
            question = instance.question if instance else None

        observation = data.get(
            "observation",
            instance.observation if instance else "",
        )
        action_required = data.get(
            "action_required",
            instance.action_required if instance else "",
        )

        if inspection is None:
            raise serializers.ValidationError({
                "inspection": "This field is required."
            })

        if not action_required or not action_required.strip():
            raise serializers.ValidationError({
                "action_required": "Action Required is mandatory."
            })

        if question is None:
            if not observation or not observation.strip():
                raise serializers.ValidationError({
                    "observation": (
                        "Enter your custom question or doubt "
                        "in Observation / Other Question."
                    )
                })
            return data

        if question.section.template_id != inspection.template_id:
            raise serializers.ValidationError({
                "question": (
                    "This question does not belong to "
                    "the inspection template."
                )
            })

        try:
            answer = InspectionAnswer.objects.get(
                inspection=inspection,
                question=question,
            )
        except InspectionAnswer.DoesNotExist:
            raise serializers.ValidationError({
                "question": (
                    "This question has not been answered "
                    "in this inspection."
                )
            })

        if answer.answer != InspectionAnswer.AnswerChoices.NO:
            raise serializers.ValidationError({
                "question": (
                    "A corrective action can only be created "
                    "for a question answered NO."
                )
            })

        if instance is None and not observation:
            data["observation"] = answer.observation

        return data

    def create(self, validated_data):
        return CorrectiveAction.objects.create(
            **validated_data,
            created_by=self.context["request"].user,
        )


class CorrectiveActionProgressSerializer(serializers.ModelSerializer):
    """Only the assigned user’s progress fields may be updated."""

    class Meta:
        model = CorrectiveAction
        fields = ["action_taken", "status"]

    def validate_status(self, value):
        instance = self.instance

        allowed_transitions = {
            CorrectiveAction.Status.OPEN: [
                CorrectiveAction.Status.IN_PROGRESS,
            ],
            CorrectiveAction.Status.IN_PROGRESS: [
                CorrectiveAction.Status.COMPLETED,
            ],
        }

        if value == instance.status:
            return value

        if value not in allowed_transitions.get(instance.status, []):
            raise serializers.ValidationError(
                f"Cannot change status from {instance.status} to {value}."
            )

        return value

    def validate(self, data):
        status = data.get("status", self.instance.status)
        action_taken = data.get(
            "action_taken",
            self.instance.action_taken,
        )

        if (
            status == CorrectiveAction.Status.COMPLETED
            and not action_taken.strip()
        ):
            raise serializers.ValidationError({
                "action_taken": (
                    "Enter the action taken before marking this "
                    "corrective action as completed."
                )
            })

        return data
