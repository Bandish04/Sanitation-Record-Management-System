from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsInspector
from .models import CorrectiveAction
from .serializers import CorrectiveActionSerializer


class CorrectiveActionListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = CorrectiveActionSerializer

    def get_queryset(self):

        return CorrectiveAction.objects.select_related(
            "inspection",
            "question",
            "assigned_to",
            "created_by",
        ).all()

    def get_permissions(self):

        if self.request.method == "POST":
            return [IsInspector()]

        return [IsAuthenticated()]