from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Plant
from .serializers import PlantSerializer


class PlantListCreateAPIView(generics.ListCreateAPIView):
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer
    permission_classes = [IsAuthenticated]