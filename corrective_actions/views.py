from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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




class CorrectiveActionDetailAPIView(
    generics.RetrieveUpdateAPIView
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

        if self.request.method in ["PUT", "PATCH"]:
            return [IsInspector()]

        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):

        corrective_action = self.get_object()

        if corrective_action.status == CorrectiveAction.Status.COMPLETED:
            raise PermissionDenied(
                "Completed corrective actions cannot be modified."
            )

        if corrective_action.status == CorrectiveAction.Status.CANCELLED:
            raise PermissionDenied(
                "Cancelled corrective actions cannot be modified."
            )

        response = super().update(
            request,
            *args,
            **kwargs,
        )

        corrective_action.refresh_from_db()

        if corrective_action.status == CorrectiveAction.Status.COMPLETED:
            if corrective_action.completed_at is None:
                corrective_action.completed_at = timezone.now()
                corrective_action.save(
                    update_fields=[
                        "completed_at",
                        "updated_at",
                    ]
                )

        return response