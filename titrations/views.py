from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import SanitizerTitration, ChloragelTitration
from .serializers import (
    SanitizerTitrationSerializer,
    ChloragelTitrationSerializer,
)


class SanitizerTitrationListCreateAPIView(
    generics.ListCreateAPIView
):
    serializer_class = SanitizerTitrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SanitizerTitration.objects.select_related(
            "plant",
            "created_by",
        ).all()

class ChloragelTitrationListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ChloragelTitrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChloragelTitration.objects.select_related(
            "plant",
            "created_by",
        ).all()