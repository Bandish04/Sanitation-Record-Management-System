from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
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

class InspectionAnswerCreateAPIView(generics.CreateAPIView):

    serializer_class = InspectionAnswerSerializer
    permission_classes = [IsInspector]

    def perform_create(self, serializer):

        inspection_id = self.request.data.get("inspection")

        try:
            inspection = SanitationInspection.objects.get(
                id=inspection_id
            )
        except SanitationInspection.DoesNotExist:
            from rest_framework.exceptions import NotFound

            raise NotFound("Inspection not found.")

        if inspection.inspector != self.request.user:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                "You can only add answers to your own inspections."
            )

        if inspection.status != SanitationInspection.Status.DRAFT:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                "Answers can only be added to draft inspections."
            )

        serializer.save(inspection=inspection)

class SanitationInspectionSubmitAPIView(generics.GenericAPIView):

    permission_classes = [IsInspector]

    def post(self, request, pk):

        try:
            inspection = SanitationInspection.objects.prefetch_related(
                "answers__question"
            ).get(pk=pk)

        except SanitationInspection.DoesNotExist:
            raise NotFound("Inspection not found.")

        # Inspector can only submit their own inspection
        if inspection.inspector != request.user:
            raise PermissionDenied(
                "You can only submit your own inspections."
            )

        # Only DRAFT inspections can be submitted
        if inspection.status != SanitationInspection.Status.DRAFT:
            raise PermissionDenied(
                "Only draft inspections can be submitted."
            )

        # Get all active questions from the inspection template
        questions = InspectionQuestion.objects.filter(
            section__template=inspection.template,
            active=True,
        )

        # Get questions that have already been answered
        answered_question_ids = set(
            inspection.answers.values_list(
                "question_id",
                flat=True,
            )
        )

        # Find unanswered questions
        unanswered_questions = []

        for question in questions:
            if question.id not in answered_question_ids:
                unanswered_questions.append(
                    question.id
                )

        # Do not allow submission if questions are missing
        if unanswered_questions:

            return Response(
                {
                    "detail": "All active inspection questions must be answered before submission.",
                    "unanswered_question_ids": unanswered_questions,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Make sure NO answers that require observations have one
        invalid_answers = []

        for answer in inspection.answers.all():

            if (
                answer.answer == InspectionAnswer.AnswerChoices.NO
                and answer.question.requires_observation_on_no
                and not answer.observation.strip()
            ):
                invalid_answers.append(answer.question_id)

        if invalid_answers:

            return Response(
                {
                    "detail": "All NO answers requiring observations must include an observation.",
                    "question_ids": invalid_answers,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Submit the inspection
        inspection.status = SanitationInspection.Status.SUBMITTED
        inspection.signed_at = timezone.now()
        inspection.save(
            update_fields=[
                "status",
                "signed_at",
                "updated_at",
            ]
        )

        return Response(
            {
                "message": "Inspection submitted successfully.",
                "inspection_id": inspection.id,
                "status": inspection.status,
                "signed_at": inspection.signed_at,
            },
            status=status.HTTP_200_OK,
        )

class ATPReportListCreateAPIView(generics.ListCreateAPIView):

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

