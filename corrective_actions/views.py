from django.contrib.auth.models import User
from django.utils import timezone

from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response

from accounts.permissions import IsInspector, IsAdmin
from audit.models import AuditLog

from .models import CorrectiveAction
from .serializers import CorrectiveActionSerializer


class IsInspectorOrAdmin(BasePermission):
    """
    Allow Inspectors or Admin users to create/update corrective actions.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return (
            IsInspector().has_permission(request, view)
            or IsAdmin().has_permission(request, view)
        )


class CorrectiveActionOptionsAPIView(generics.GenericAPIView):
    """
    Return users that can be selected for a corrective action.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        users = User.objects.filter(
            is_active=True
        ).order_by(
            "first_name",
            "last_name",
            "username",
        )

        user_list = []

        for user in users:
            if user.first_name or user.last_name:
                display_name = (
                    f"{user.first_name} {user.last_name}"
                ).strip()
                display_name = (
                    f"{display_name} ({user.username})"
                )
            else:
                display_name = user.username

            user_list.append(
                {
                    "id": user.id,
                    "username": user.username,
                    "name": display_name,
                }
            )

        return Response(
            {
                "users": user_list,
            }
        )


class CorrectiveActionListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CorrectiveActionSerializer

    def get_queryset(self):
        queryset = CorrectiveAction.objects.select_related(
            "inspection",
            "question",
            "assigned_to",
            "created_by",
        ).all()

        status_filter = self.request.query_params.get("status")

        if status_filter:
            queryset = queryset.filter(
                status=status_filter
            )

        return queryset

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsInspectorOrAdmin()]

        return [IsAuthenticated()]

    def perform_create(self, serializer):
        corrective_action = serializer.save()

        AuditLog.objects.create(
            user=self.request.user,
            action="CREATE_CORRECTIVE_ACTION",
            object_type="CorrectiveAction",
            object_id=corrective_action.id,
            old_values=None,
            new_values={
                "inspection": corrective_action.inspection_id,
                "question": corrective_action.question_id,
                "observation": corrective_action.observation,
                "action_required": corrective_action.action_required,
                "assigned_to": (
                    corrective_action.assigned_to_id
                    if corrective_action.assigned_to
                    else None
                ),
                "due_date": (
                    str(corrective_action.due_date)
                    if corrective_action.due_date
                    else None
                ),
                "action_taken": corrective_action.action_taken,
                "status": corrective_action.status,
            },
            reason="Corrective action created.",
        )


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
            return [IsInspectorOrAdmin()]

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

        old_values = {
            "inspection": corrective_action.inspection_id,
            "question": corrective_action.question_id,
            "observation": corrective_action.observation,
            "action_required": corrective_action.action_required,
            "assigned_to": (
                corrective_action.assigned_to_id
                if corrective_action.assigned_to
                else None
            ),
            "due_date": (
                str(corrective_action.due_date)
                if corrective_action.due_date
                else None
            ),
            "action_taken": corrective_action.action_taken,
            "status": corrective_action.status,
        }

        response = super().update(
            request,
            *args,
            **kwargs,
        )

        corrective_action.refresh_from_db()

        if (
            corrective_action.status
            == CorrectiveAction.Status.COMPLETED
        ):
            if corrective_action.completed_at is None:
                corrective_action.completed_at = timezone.now()

                corrective_action.save(
                    update_fields=[
                        "completed_at",
                        "updated_at",
                    ]
                )

        new_values = {
            "inspection": corrective_action.inspection_id,
            "question": corrective_action.question_id,
            "observation": corrective_action.observation,
            "action_required": corrective_action.action_required,
            "assigned_to": (
                corrective_action.assigned_to_id
                if corrective_action.assigned_to
                else None
            ),
            "due_date": (
                str(corrective_action.due_date)
                if corrective_action.due_date
                else None
            ),
            "action_taken": corrective_action.action_taken,
            "status": corrective_action.status,
        }

        AuditLog.objects.create(
            user=request.user,
            action="UPDATE_CORRECTIVE_ACTION",
            object_type="CorrectiveAction",
            object_id=corrective_action.id,
            old_values=old_values,
            new_values=new_values,
            reason="Corrective action updated.",
        )

        return response