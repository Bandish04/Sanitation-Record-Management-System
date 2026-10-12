from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response

from accounts.permissions import IsInspector, IsAdmin
from audit.models import AuditLog

from .models import CorrectiveAction
from .serializers import (
    CorrectiveActionSerializer,
    CorrectiveActionProgressSerializer,
)


class IsInspectorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return (
            IsInspector().has_permission(request, view)
            or IsAdmin().has_permission(request, view)
        )


def action_values(action):
    return {
        "inspection": action.inspection_id,
        "question": action.question_id,
        "is_custom_question": action.is_custom_question,
        "observation": action.observation,
        "action_required": action.action_required,
        "assigned_to": action.assigned_to_id,
        "due_date": str(action.due_date) if action.due_date else None,
        "action_taken": action.action_taken,
        "status": action.status,
    }


def write_action_audit(request, action, old_values, new_values, reason):
    AuditLog.objects.create(
        user=request.user,
        action="UPDATE_CORRECTIVE_ACTION",
        object_type="CorrectiveAction",
        object_id=action.id,
        old_values=old_values,
        new_values=new_values,
        reason=reason,
    )


class CorrectiveActionOptionsAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        users = User.objects.filter(
            is_active=True
        ).order_by("first_name", "last_name", "username")

        user_list = []

        for user in users:
            if user.first_name or user.last_name:
                display_name = (
                    f"{user.first_name} {user.last_name}"
                ).strip()
                display_name = f"{display_name} ({user.username})"
            else:
                display_name = user.username

            user_list.append({
                "id": user.id,
                "username": user.username,
                "name": display_name,
            })

        return Response({"users": user_list})


class CorrectiveActionListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CorrectiveActionSerializer

    def get_queryset(self):
        queryset = CorrectiveAction.objects.select_related(
            "inspection",
            "inspection__plant",
            "inspection__template",
            "question",
            "assigned_to",
            "created_by",
        ).all()

        status_filter = self.request.query_params.get("status")

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsInspectorOrAdmin()]

        return [IsAuthenticated()]

    @transaction.atomic
    def perform_create(self, serializer):
        action = serializer.save()

        AuditLog.objects.create(
            user=self.request.user,
            action="CREATE_CORRECTIVE_ACTION",
            object_type="CorrectiveAction",
            object_id=action.id,
            old_values=None,
            new_values=action_values(action),
            reason="Corrective action created.",
        )


class CorrectiveActionDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = CorrectiveActionSerializer

    def get_queryset(self):
        return CorrectiveAction.objects.select_related(
            "inspection",
            "inspection__plant",
            "inspection__template",
            "question",
            "assigned_to",
            "created_by",
        ).all()

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            return [IsInspectorOrAdmin()]

        return [IsAuthenticated()]

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        action = self.get_object()

        if action.status in [
            CorrectiveAction.Status.COMPLETED,
            CorrectiveAction.Status.CANCELLED,
        ]:
            raise PermissionDenied(
                "Completed or cancelled corrective actions cannot be modified."
            )

        old_values = action_values(action)

        response = super().update(request, *args, **kwargs)
        action.refresh_from_db()

        if (
            action.status == CorrectiveAction.Status.COMPLETED
            and action.completed_at is None
        ):
            action.completed_at = timezone.now()
            action.save(update_fields=["completed_at", "updated_at"])

        write_action_audit(
            request,
            action,
            old_values,
            action_values(action),
            "Corrective action updated.",
        )

        return response


class CorrectiveActionProgressAPIView(generics.UpdateAPIView):
    """Allow an assignee to update only action_taken and status."""

    serializer_class = CorrectiveActionProgressSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch", "put", "options", "head"]

    def get_queryset(self):
        return CorrectiveAction.objects.select_related(
            "inspection",
            "inspection__plant",
            "assigned_to",
            "created_by",
        ).filter(assigned_to=self.request.user)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        action = self.get_object()

        if action.status in [
            CorrectiveAction.Status.COMPLETED,
            CorrectiveAction.Status.CANCELLED,
        ]:
            raise PermissionDenied(
                "Completed or cancelled corrective actions cannot be modified."
            )

        forbidden_fields = set(request.data.keys()) - {
            "action_taken",
            "status",
        }

        if forbidden_fields:
            raise ValidationError({
                "detail": (
                    "Assigned users may update only Action Taken and Status."
                )
            })

        old_values = action_values(action)

        response = super().update(request, *args, **kwargs)
        action.refresh_from_db()

        if (
            action.status == CorrectiveAction.Status.COMPLETED
            and action.completed_at is None
        ):
            action.completed_at = timezone.now()
            action.save(update_fields=["completed_at", "updated_at"])

        write_action_audit(
            request,
            action,
            old_values,
            action_values(action),
            "Assigned user updated corrective-action progress.",
        )

        return response
