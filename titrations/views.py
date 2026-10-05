from django.utils import timezone

from rest_framework import generics, status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsInspectorTeamLeadAdmin
from audit.models import AuditLog

from .models import (
    SanitizerTitration,
    ChloragelTitration,
)
from .serializers import (
    SanitizerTitrationSerializer,
    ChloragelTitrationSerializer,
)


# ============================================================
# SANITIZER TITRATION
# ============================================================


class SanitizerTitrationListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = SanitizerTitrationSerializer

    def get_queryset(self):
        return SanitizerTitration.objects.select_related(
            "plant",
            "created_by",
        ).all()

    def get_permissions(self):

        if self.request.method == "POST":
            return [IsInspectorTeamLeadAdmin()]

        return [IsAuthenticated()]

    def perform_create(self, serializer):

        titration = serializer.save(
        
        )

        AuditLog.objects.create(
            user=self.request.user,
            action="CREATE_TITRATION",
            object_type="SanitizerTitration",
            object_id=titration.id,
            old_values=None,
            new_values={
                "plant": titration.plant_id,
                "r71_drops": titration.r71_drops,
                "ppm": str(titration.ppm),
                "percent_vv": str(
                    titration.percent_vv
                ),
                "status": titration.status,
                "result_status": titration.result_status,
            },
            reason="Sanitizer titration created.",
        )


class SanitizerTitrationDetailAPIView(
    generics.RetrieveUpdateAPIView
):

    serializer_class = SanitizerTitrationSerializer

    def get_queryset(self):
        return SanitizerTitration.objects.select_related(
            "plant",
            "created_by",
        ).all()

    def get_permissions(self):

        if self.request.method in [
            "PUT",
            "PATCH",
        ]:
            return [IsInspectorTeamLeadAdmin()]

        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):

        titration = self.get_object()

        is_admin = request.user.groups.filter(
            name="Admin"
        ).exists()

        # Inspectors and Team Leads can only edit
        # their own records.
        #
        # Admins can edit any record.
        if (
            not is_admin
            and titration.created_by != request.user
        ):
            raise PermissionDenied(
                "You can only edit your own titrations."
            )

        # Submitted records are locked.
        if titration.status != (
            SanitizerTitration.Status.DRAFT
        ):
            raise PermissionDenied(
                "Only draft titrations can be modified."
            )

        old_values = {
            "plant": titration.plant_id,
            "r71_drops": titration.r71_drops,
            "ppm": str(titration.ppm),
            "percent_vv": str(
                titration.percent_vv
            ),
            "status": titration.status,
            "result_status": titration.result_status,
        }

        response = super().update(
            request,
            *args,
            **kwargs,
        )

        titration.refresh_from_db()

        new_values = {
            "plant": titration.plant_id,
            "r71_drops": titration.r71_drops,
            "ppm": str(titration.ppm),
            "percent_vv": str(
                titration.percent_vv
            ),
            "status": titration.status,
            "result_status": titration.result_status,
        }

        AuditLog.objects.create(
            user=request.user,
            action="EDIT_TITRATION",
            object_type="SanitizerTitration",
            object_id=titration.id,
            old_values=old_values,
            new_values=new_values,
            reason="Sanitizer titration edited.",
        )

        return response


class SanitizerTitrationSubmitAPIView(
    generics.GenericAPIView
):

    permission_classes = [
        IsInspectorTeamLeadAdmin
    ]

    def post(self, request, pk):

        try:
            titration = SanitizerTitration.objects.get(
                pk=pk
            )

        except SanitizerTitration.DoesNotExist:
            raise NotFound(
                "Sanitizer titration not found."
            )

        is_admin = request.user.groups.filter(
            name="Admin"
        ).exists()

        # Inspectors and Team Leads can only submit
        # their own records.
        #
        # Admins can submit any record.
        if (
            not is_admin
            and titration.created_by != request.user
        ):
            raise PermissionDenied(
                "You can only submit your own titrations."
            )

        # Only DRAFT records can be submitted.
        if titration.status != (
            SanitizerTitration.Status.DRAFT
        ):
            raise PermissionDenied(
                "Only draft titrations can be submitted."
            )

        old_values = {
            "status": titration.status,
            "result_status": titration.result_status,
            "submitted_at": None,
        }

        titration.status = (
            SanitizerTitration.Status.SUBMITTED
        )

        titration.submitted_at = timezone.now()

        titration.save(
            update_fields=[
                "status",
                "submitted_at",
                "updated_at",
            ]
        )

        new_values = {
            "status": titration.status,
            "result_status": titration.result_status,
            "submitted_at": (
                titration.submitted_at.isoformat()
            ),
        }

        AuditLog.objects.create(
            user=request.user,
            action="SUBMIT_TITRATION",
            object_type="SanitizerTitration",
            object_id=titration.id,
            old_values=old_values,
            new_values=new_values,
            reason="Sanitizer titration submitted.",
        )

        return Response(
            {
                "message": (
                    "Sanitizer titration "
                    "submitted successfully."
                ),
                "titration_id": titration.id,
                "status": titration.status,
                "result_status": titration.result_status,
                "submitted_at": titration.submitted_at,
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# CHLORAGEL TITRATION
# ============================================================


class ChloragelTitrationListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = ChloragelTitrationSerializer

    def get_queryset(self):
        return ChloragelTitration.objects.select_related(
            "plant",
            "created_by",
        ).all()

    def get_permissions(self):

        if self.request.method == "POST":
            return [IsInspectorTeamLeadAdmin()]

        return [IsAuthenticated()]

    def perform_create(self, serializer):

        titration = serializer.save(
           
        )

        AuditLog.objects.create(
            user=self.request.user,
            action="CREATE_TITRATION",
            object_type="ChloragelTitration",
            object_id=titration.id,
            old_values=None,
            new_values={
                "plant": titration.plant_id,
                "r9_drops": titration.r9_drops,
                "result_percent": str(
                    titration.result_percent
                ),
                "status": titration.status,
                "result_status": titration.result_status,
            },
            reason="Chloragel titration created.",
        )


class ChloragelTitrationDetailAPIView(
    generics.RetrieveUpdateAPIView
):

    serializer_class = ChloragelTitrationSerializer

    def get_queryset(self):
        return ChloragelTitration.objects.select_related(
            "plant",
            "created_by",
        ).all()

    def get_permissions(self):

        if self.request.method in [
            "PUT",
            "PATCH",
        ]:
            return [IsInspectorTeamLeadAdmin()]

        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):

        titration = self.get_object()

        is_admin = request.user.groups.filter(
            name="Admin"
        ).exists()

        # Inspectors and Team Leads can only edit
        # their own records.
        #
        # Admins can edit any record.
        if (
            not is_admin
            and titration.created_by != request.user
        ):
            raise PermissionDenied(
                "You can only edit your own titrations."
            )

        # Submitted records are locked.
        if titration.status != (
            ChloragelTitration.Status.DRAFT
        ):
            raise PermissionDenied(
                "Only draft titrations can be modified."
            )

        old_values = {
            "plant": titration.plant_id,
            "r9_drops": titration.r9_drops,
            "result_percent": str(
                titration.result_percent
            ),
            "status": titration.status,
            "result_status": titration.result_status,
        }

        response = super().update(
            request,
            *args,
            **kwargs,
        )

        titration.refresh_from_db()

        new_values = {
            "plant": titration.plant_id,
            "r9_drops": titration.r9_drops,
            "result_percent": str(
                titration.result_percent
            ),
            "status": titration.status,
            "result_status": titration.result_status,
        }

        AuditLog.objects.create(
            user=request.user,
            action="EDIT_TITRATION",
            object_type="ChloragelTitration",
            object_id=titration.id,
            old_values=old_values,
            new_values=new_values,
            reason="Chloragel titration edited.",
        )

        return response


class ChloragelTitrationSubmitAPIView(
    generics.GenericAPIView
):

    permission_classes = [
        IsInspectorTeamLeadAdmin
    ]

    def post(self, request, pk):

        try:
            titration = ChloragelTitration.objects.get(
                pk=pk
            )

        except ChloragelTitration.DoesNotExist:
            raise NotFound(
                "Chloragel titration not found."
            )

        is_admin = request.user.groups.filter(
            name="Admin"
        ).exists()

        # Inspectors and Team Leads can only submit
        # their own records.
        #
        # Admins can submit any record.
        if (
            not is_admin
            and titration.created_by != request.user
        ):
            raise PermissionDenied(
                "You can only submit your own titrations."
            )

        # Only DRAFT records can be submitted.
        if titration.status != (
            ChloragelTitration.Status.DRAFT
        ):
            raise PermissionDenied(
                "Only draft titrations can be submitted."
            )

        old_values = {
            "status": titration.status,
            "result_status": titration.result_status,
            "submitted_at": None,
        }

        titration.status = (
            ChloragelTitration.Status.SUBMITTED
        )

        titration.submitted_at = timezone.now()

        titration.save(
            update_fields=[
                "status",
                "submitted_at",
                "updated_at",
            ]
        )

        new_values = {
            "status": titration.status,
            "result_status": titration.result_status,
            "submitted_at": (
                titration.submitted_at.isoformat()
            ),
        }

        AuditLog.objects.create(
            user=request.user,
            action="SUBMIT_TITRATION",
            object_type="ChloragelTitration",
            object_id=titration.id,
            old_values=old_values,
            new_values=new_values,
            reason="Chloragel titration submitted.",
        )

        return Response(
            {
                "message": (
                    "Chloragel titration "
                    "submitted successfully."
                ),
                "titration_id": titration.id,
                "status": titration.status,
                "result_status": titration.result_status,
                "submitted_at": titration.submitted_at,
            },
            status=status.HTTP_200_OK,
        )