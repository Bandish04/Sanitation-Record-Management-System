from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import (
    InspectionTemplate,
    InspectionSection,
    InspectionQuestion,
)

from .serializers import (
    InspectionTemplateSerializer,
    InspectionSectionSerializer,
    InspectionQuestionSerializer,
)

from accounts.permissions import IsAdmin


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