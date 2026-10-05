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

    question_text = serializers.CharField(
        source="question.question_text",
        read_only=True,
    )

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

            "assigned_to_username",

            "created_by",
            "created_by_username",

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

    def get_inspection_display(self, obj):

        if not obj.inspection:
            return ""

        plant_name = ""

        if obj.inspection.plant:
            plant_name = obj.inspection.plant.name

        template_name = ""

        if obj.inspection.template:
            template_name = obj.inspection.template.name

        inspection_date = (
            str(obj.inspection.inspection_date)
            if obj.inspection.inspection_date
            else ""
        )

        parts = []

        if plant_name:
            parts.append(plant_name)

        if template_name:
            parts.append(template_name)

        if inspection_date:
            parts.append(inspection_date)

        return " - ".join(parts)

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

        inspection = data.get(
            "inspection",
            self.instance.inspection
            if self.instance
            else None,
        )

        question = data.get(
            "question",
            self.instance.question
            if self.instance
            else None,
        )

        if inspection is None:

            raise serializers.ValidationError(
                {
                    "inspection":
                    "This field is required."
                }
            )

        if question is None:

            raise serializers.ValidationError(
                {
                    "question":
                    "This field is required."
                }
            )

        if question.section.template_id != inspection.template_id:

            raise serializers.ValidationError(
                {
                    "question": (
                        "This question does not belong "
                        "to the inspection template."
                    )
                }
            )

        try:

            answer = InspectionAnswer.objects.get(
                inspection=inspection,
                question=question,
            )

        except InspectionAnswer.DoesNotExist:

            raise serializers.ValidationError(
                {
                    "question": (
                        "This question has not been "
                        "answered in this inspection."
                    )
                }
            )

        if answer.answer != InspectionAnswer.AnswerChoices.NO:

            raise serializers.ValidationError(
                {
                    "question": (
                        "A corrective action can only "
                        "be created for a question "
                        "answered NO."
                    )
                }
            )

        if self.instance is None:

            if not data.get("observation"):

                data["observation"] = (
                    answer.observation
                )

        return data

    def create(self, validated_data):

        return CorrectiveAction.objects.create(
            **validated_data,
            created_by=self.context[
                "request"
            ].user,
        )