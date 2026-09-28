from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdmin

from .models import Plant
from .serializers import PlantSerializer


class PlantListCreateAPIView(generics.ListCreateAPIView):

    queryset = Plant.objects.all()
    serializer_class = PlantSerializer

    def get_permissions(self):

        if self.request.method == "POST":
            return [IsAdmin()]

        return [IsAuthenticated()]