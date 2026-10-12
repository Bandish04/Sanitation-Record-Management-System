
from rest_framework import generics

from accounts.permissions import IsAdmin
from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogListAPIView(generics.ListAPIView):

    serializer_class = AuditLogSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return AuditLog.objects.select_related(
            "user",
        ).order_by(
            "-timestamp",
        )
