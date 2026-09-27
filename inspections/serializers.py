from rest_framework import serializers

from .models import (
    InspectionTemplate,
    InspectionSection,
    InspectionQuestion,
    SanitationInspection,
    InspectionAnswer,
    ATPReport,
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

class InspectionAnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = InspectionAnswer

        fields = [
            "id",
            "inspection",
            "question",
            "answer",
            "observation",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "inspection",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):

        answer = data.get("answer")
        observation = data.get("observation", "").strip()

        question = data.get("question")

        if (
            answer == InspectionAnswer.AnswerChoices.NO
            and question.requires_observation_on_no
            and not observation
        ):
            raise serializers.ValidationError(
                {
                    "observation": (
                        "An observation is required "
                        "when the answer is NO."
                    )
                }
            )

        return data

class SanitationInspectionSerializer(serializers.ModelSerializer):

    answers = InspectionAnswerSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = SanitationInspection

        fields = [
            "id",
            "plant",
            "template",
            "inspection_date",
            "inspector",
            "status",
            "general_notes",
            "signed_at",
            "answers",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "inspector",
            "status",
            "signed_at",
            "answers",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):

        return SanitationInspection.objects.create(
            **validated_data,
            inspector=self.context["request"].user,
            status=SanitationInspection.Status.DRAFT,
        )


class ATPReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = ATPReport
        fields = [
            "id",
            "plant",
            "inspection",
            "file",
            "original_filename",
            "uploaded_by",
            "uploaded_at",
            "status",
            "notes",
        ]

        read_only_fields = [
            "id",
            "original_filename",
            "uploaded_by",
            "uploaded_at",
            "status",
        ]

    def validate_file(self, file):

        allowed_extensions = [
            ".pdf",
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        ]

        filename = file.name.lower()

        if not any(
            filename.endswith(extension)
            for extension in allowed_extensions
        ):
            raise serializers.ValidationError(
                "Only PDF, JPG, JPEG, PNG, and WEBP files are allowed."
            )

        # 10 MB maximum file size
        max_size = 10 * 1024 * 1024

        if file.size > max_size:
            raise serializers.ValidationError(
                "File size cannot exceed 10 MB."
            )

        return file

    def create(self, validated_data):

        uploaded_file = validated_data["file"]

        return ATPReport.objects.create(
            **validated_data,
            original_filename=uploaded_file.name,
            uploaded_by=self.context["request"].user,
            status=ATPReport.Status.ACTIVE,
        )