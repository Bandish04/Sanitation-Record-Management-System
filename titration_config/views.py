from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdmin

from .models import TitrationLimit
from .serializers import TitrationLimitSerializer


class TitrationLimitListCreateAPIView(
    generics.ListCreateAPIView
):
    serializer_class = TitrationLimitSerializer

    def get_queryset(self):
        return TitrationLimit.objects.select_related(
            "plant",
        ).all()

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdmin()]

        return [IsAuthenticated()]


class TitrationLimitDetailAPIView(
    generics.RetrieveUpdateAPIView
):
    serializer_class = TitrationLimitSerializer

    def get_queryset(self):
        return TitrationLimit.objects.select_related(
            "plant",
        ).all()

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            return [IsAdmin()]

        return [IsAuthenticated()]