
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound

from .models import (
    InspectionTemplate,
    InspectionSection,
    InspectionQuestion,
    SanitationInspection,
    InspectionAnswer,
    ATPReport,
)

from .serializers import (
    InspectionTemplateSerializer,
    InspectionSectionSerializer,
    InspectionQuestionSerializer,
    SanitationInspectionSerializer,
    InspectionAnswerSerializer,
    ATPReportSerializer,
)

from accounts.permissions import IsAdmin, IsInspector
from audit.models import AuditLog


# ============================================================
# INSPECTION TEMPLATES
# ============================================================

class InspectionTemplateListCreateAPIView(
    generics.ListCreateAPIView
):
    queryset = InspectionTemplate.objects.all()
    serializer_class = InspectionTemplateSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdmin()]

        return [IsAuthenticated()]


# ============================================================
# INSPECTION SECTIONS
# ============================================================

class InspectionSectionListCreateAPIView(
    generics.ListCreateAPIView
):
    queryset = InspectionSection.objects.select_related(
        "template"
    ).all()

    serializer_class = InspectionSectionSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdmin()]

        return [IsAuthenticated()]


# ============================================================
# INSPECTION QUESTIONS
# ============================================================

class InspectionQuestionListCreateAPIView(
    generics.ListCreateAPIView
):
    queryset = InspectionQuestion.objects.select_related(
        "section"
    ).all()

    serializer_class = InspectionQuestionSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdmin()]

        return [IsAuthenticated()]


# ============================================================
# SANITATION INSPECTION LIST + CREATE
# ============================================================

class SanitationInspectionListCreateAPIView(
    generics.ListCreateAPIView
):
    serializer_class = SanitationInspectionSerializer

    def get_queryset(self):
        return SanitationInspection.objects.select_related(
            "plant",
            "template",
            "inspector",
        ).prefetch_related(
            "answers__question"
        ).all()

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsInspector()]

        return [IsAuthenticated()]

    def perform_create(self, serializer):
        inspection = serializer.save()

        AuditLog.objects.create(
            user=self.request.user,
            action="CREATE_INSPECTION",
            object_type="SanitationInspection",
            object_id=inspection.id,
            old_values=None,
            new_values={
                "plant": inspection.plant_id,
                "template": inspection.template_id,
                "inspection_date": str(
                    inspection.inspection_date
                ),
                "inspector": inspection.inspector_id,
                "status": inspection.status,
                "general_notes": inspection.general_notes,
            },
            reason="Sanitation inspection created.",
        )


# ============================================================
# SANITATION INSPECTION DETAIL + EDIT
# ============================================================

class SanitationInspectionDetailAPIView(
    generics.RetrieveUpdateAPIView
):
    serializer_class = SanitationInspectionSerializer

    def get_queryset(self):
        return SanitationInspection.objects.select_related(
            "plant",
            "template",
            "inspector",
        ).prefetch_related(
            "answers__question"
        ).all()

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            return [IsInspector()]

        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        inspection = self.get_object()

        # Only the inspector who created the inspection
        # can edit it.
        if inspection.inspector != request.user:
            raise PermissionDenied(
                "You can only edit your own inspections."
            )

        # Only draft inspections can be edited.
        if inspection.status != SanitationInspection.Status.DRAFT:
            raise PermissionDenied(
                "Only draft inspections can be modified."
            )

        # Store old values before modification.
        old_values = {
            "plant": inspection.plant_id,
            "template": inspection.template_id,
            "inspection_date": str(
                inspection.inspection_date
            ),
            "status": inspection.status,
            "general_notes": inspection.general_notes,
        }

        # Perform the actual update.
        response = super().update(
            request,
            *args,
            **kwargs,
        )

        # Reload the object after the update.
        inspection.refresh_from_db()

        # Store new values after modification.
        new_values = {
            "plant": inspection.plant_id,
            "template": inspection.template_id,
            "inspection_date": str(
                inspection.inspection_date
            ),
            "status": inspection.status,
            "general_notes": inspection.general_notes,
        }

        # Create audit record.
        AuditLog.objects.create(
            user=request.user,
            action="EDIT_INSPECTION",
            object_type="SanitationInspection",
            object_id=inspection.id,
            old_values=old_values,
            new_values=new_values,
            reason="Sanitation inspection edited.",
        )

        return response


# ============================================================
# INSPECTION ANSWER CREATE
# ============================================================

class InspectionAnswerCreateAPIView(
    generics.CreateAPIView
):
    serializer_class = InspectionAnswerSerializer
    permission_classes = [IsInspector]

    def perform_create(self, serializer):

        inspection_id = self.request.data.get(
            "inspection"
        )

        try:
            inspection = SanitationInspection.objects.get(
                id=inspection_id
            )

        except SanitationInspection.DoesNotExist:
            raise NotFound(
                "Inspection not found."
            )

        # Inspector can only add answers
        # to their own inspection.
        if inspection.inspector != self.request.user:
            raise PermissionDenied(
                "You can only add answers to your own inspections."
            )

        # Answers can only be added while
        # the inspection is still a draft.
        if inspection.status != SanitationInspection.Status.DRAFT:
            raise PermissionDenied(
                "Answers can only be added to draft inspections."
            )

        serializer.save(
            inspection=inspection
        )


# ============================================================
# INSPECTION ANSWER DETAIL + EDIT
# ============================================================

class InspectionAnswerDetailAPIView(
    generics.RetrieveUpdateAPIView
):
    serializer_class = InspectionAnswerSerializer

    def get_queryset(self):
        return InspectionAnswer.objects.select_related(
            "inspection",
            "question",
        ).all()

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            return [IsInspector()]

        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):

        answer = self.get_object()

        # Only the inspector who owns
        # the inspection can edit its answers.
        if answer.inspection.inspector != request.user:
            raise PermissionDenied(
                "You can only edit your own inspection answers."
            )

        # Answers can only be modified
        # while the inspection is a draft.
        if (
            answer.inspection.status
            != SanitationInspection.Status.DRAFT
        ):
            raise PermissionDenied(
                "Answers can only be modified while the inspection is in draft."
            )

        return super().update(
            request,
            *args,
            **kwargs,
        )


# ============================================================
# SANITATION INSPECTION SUBMIT
# ============================================================

class SanitationInspectionSubmitAPIView(
    generics.GenericAPIView
):
    permission_classes = [IsInspector]

    def post(self, request, pk):

        try:
            inspection = (
                SanitationInspection.objects
                .prefetch_related(
                    "answers__question"
                )
                .get(pk=pk)
            )

        except SanitationInspection.DoesNotExist:
            raise NotFound(
                "Inspection not found."
            )

        # ----------------------------------------------------
        # Inspector ownership check
        # ----------------------------------------------------

        if inspection.inspector != request.user:
            raise PermissionDenied(
                "You can only submit your own inspections."
            )

        # ----------------------------------------------------
        # Only draft inspections can be submitted
        # ----------------------------------------------------

        if inspection.status != SanitationInspection.Status.DRAFT:
            raise PermissionDenied(
                "Only draft inspections can be submitted."
            )

        # ----------------------------------------------------
        # Get all active questions from the template
        # ----------------------------------------------------

        questions = InspectionQuestion.objects.filter(
            section__template=inspection.template,
            active=True,
        )

        # ----------------------------------------------------
        # Get questions already answered
        # ----------------------------------------------------

        answered_question_ids = set(
            inspection.answers.values_list(
                "question_id",
                flat=True,
            )
        )

        # ----------------------------------------------------
        # Find unanswered questions
        # ----------------------------------------------------

        unanswered_questions = []

        for question in questions:

            if question.id not in answered_question_ids:
                unanswered_questions.append(
                    question.id
                )

        # ----------------------------------------------------
        # Prevent submission if questions are missing
        # ----------------------------------------------------

        if unanswered_questions:

            return Response(
                {
                    "detail": (
                        "All active inspection questions must "
                        "be answered before submission."
                    ),
                    "unanswered_question_ids": (
                        unanswered_questions
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ----------------------------------------------------
        # Validate NO answers requiring observations
        # ----------------------------------------------------

        invalid_answers = []

        for answer in inspection.answers.all():

            if (
                answer.answer
                == InspectionAnswer.AnswerChoices.NO
                and answer.question.requires_observation_on_no
                and not answer.observation.strip()
            ):
                invalid_answers.append(
                    answer.question_id
                )

        # ----------------------------------------------------
        # Prevent submission if required observations missing
        # ----------------------------------------------------

        if invalid_answers:

            return Response(
                {
                    "detail": (
                        "All NO answers requiring observations "
                        "must include an observation."
                    ),
                    "question_ids": invalid_answers,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ----------------------------------------------------
        # Store old values for audit
        # ----------------------------------------------------

        old_values = {
            "status": inspection.status,
            "signed_at": (
                inspection.signed_at.isoformat()
                if inspection.signed_at
                else None
            ),
        }

        # ----------------------------------------------------
        # Submit the inspection
        # ----------------------------------------------------

        inspection.status = (
            SanitationInspection.Status.SUBMITTED
        )

        inspection.signed_at = timezone.now()

        inspection.save(
            update_fields=[
                "status",
                "signed_at",
                "updated_at",
            ]
        )

        # ----------------------------------------------------
        # Create submission audit log
        # ----------------------------------------------------

        AuditLog.objects.create(
            user=request.user,
            action="SUBMIT_INSPECTION",
            object_type="SanitationInspection",
            object_id=inspection.id,
            old_values=old_values,
            new_values={
                "status": inspection.status,
                "signed_at": (
                    inspection.signed_at.isoformat()
                ),
            },
            reason="Sanitation inspection submitted.",
        )

        # ----------------------------------------------------
        # Return successful response
        # ----------------------------------------------------

        return Response(
            {
                "message": (
                    "Inspection submitted successfully."
                ),
                "inspection_id": inspection.id,
                "status": inspection.status,
                "signed_at": inspection.signed_at,
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# ATP REPORTS
# ============================================================

class ATPReportListCreateAPIView(
    generics.ListCreateAPIView
):
    serializer_class = ATPReportSerializer

    def get_queryset(self):
        return ATPReport.objects.select_related(
            "plant",
            "inspection",
            "uploaded_by",
        ).all()

    def get_permissions(self):

        if self.request.method == "POST":
            return [IsAdmin()]

        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save()



class SanitationInspectionCorrectionAPIView(
    generics.UpdateAPIView
):
    serializer_class = SanitationInspectionSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return SanitationInspection.objects.select_related(
            "plant",
            "template",
            "inspector",
        ).prefetch_related(
            "answers__question"
        ).all()

    def update(self, request, *args, **kwargs):
        inspection = self.get_object()

        # Only submitted inspections can be corrected.
        if inspection.status != SanitationInspection.Status.SUBMITTED:
            raise PermissionDenied(
                "Only submitted inspections can be corrected."
            )

        # A correction reason is required.
        reason = request.data.get("reason")

        if not reason or not str(reason).strip():
            return Response(
                {
                    "detail": "A correction reason is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Store the original values before correction.
        old_values = {
            "plant": inspection.plant_id,
            "template": inspection.template_id,
            "inspection_date": str(
                inspection.inspection_date
            ),
            "status": inspection.status,
            "general_notes": inspection.general_notes,
        }

        # Remove "reason" before passing data to the serializer.
        correction_data = request.data.copy()
        correction_data.pop("reason", None)

        serializer = self.get_serializer(
            inspection,
            data=correction_data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)
        serializer.save(
            status=SanitationInspection.Status.CORRECTED
        )

        inspection.refresh_from_db()

        # Store the corrected values.
        new_values = {
            "plant": inspection.plant_id,
            "template": inspection.template_id,
            "inspection_date": str(
                inspection.inspection_date
            ),
            "status": inspection.status,
            "general_notes": inspection.general_notes,
        }

        # Create audit record.
        AuditLog.objects.create(
            user=request.user,
            action="ADMIN_CORRECTION",
            object_type="SanitationInspection",
            object_id=inspection.id,
            old_values=old_values,
            new_values=new_values,
            reason=str(reason).strip(),
        )

        return Response(
            {
                "message": (
                    "Sanitation inspection corrected successfully."
                ),
                "inspection": SanitationInspectionSerializer(
                    inspection
                ).data,
            },
            status=status.HTTP_200_OK,
        )


