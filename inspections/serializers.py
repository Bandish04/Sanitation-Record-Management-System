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

        # ----------------------------------------------------
        # GET INSPECTION
        # ----------------------------------------------------
        if self.instance is None:
            inspection_id = self.context["request"].data.get(
                "inspection"
            )

            if not inspection_id:
                raise serializers.ValidationError(
                    {
                        "inspection": (
                            "Inspection is required."
                        )
                    }
                )

            try:
                inspection = SanitationInspection.objects.get(
                    id=inspection_id
                )
            except SanitationInspection.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        "inspection": (
                            "Inspection does not exist."
                        )
                    }
                )

        else:
            inspection = self.instance.inspection

        # ----------------------------------------------------
        # GET QUESTION
        # ----------------------------------------------------
        question = data.get(
            "question",
            self.instance.question
            if self.instance
            else None,
        )

        if question is None:
            raise serializers.ValidationError(
                {
                    "question": (
                        "Question is required."
                    )
                }
            )

        # ----------------------------------------------------
        # MAKE SURE QUESTION BELONGS TO TEMPLATE
        # ----------------------------------------------------
        if (
            question.section.template_id
            != inspection.template_id
        ):
            raise serializers.ValidationError(
                {
                    "question": (
                        "This question does not belong "
                        "to the inspection template."
                    )
                }
            )

        # ----------------------------------------------------
        # PREVENT DUPLICATE ANSWERS
        # ----------------------------------------------------
        existing_answer = (
            InspectionAnswer.objects
            .filter(
                inspection=inspection,
                question=question,
            )
            .exclude(
                pk=self.instance.pk
            )
            .first()
            if self.instance
            else InspectionAnswer.objects.filter(
                inspection=inspection,
                question=question,
            ).first()
        )

        if existing_answer:
            raise serializers.ValidationError(
                {
                    "question": (
                        "This question has already "
                        "been answered for this inspection."
                    )
                }
            )

        # ----------------------------------------------------
        # GET ANSWER
        # ----------------------------------------------------
        answer = data.get(
            "answer",
            self.instance.answer
            if self.instance
            else None,
        )

        # ----------------------------------------------------
        # GET OBSERVATION
        # ----------------------------------------------------
        observation = data.get(
            "observation",
            self.instance.observation
            if self.instance
            else "",
        )

        observation = observation.strip()

        # ----------------------------------------------------
        # NO ANSWER REQUIRES OBSERVATION
        # ----------------------------------------------------
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