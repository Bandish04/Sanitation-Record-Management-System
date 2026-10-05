from django.urls import path

from .views import (
    PlantDetailAPIView,
    PlantListCreateAPIView,
)


urlpatterns = [

    path(
        "",
        PlantListCreateAPIView.as_view(),
        name="plant-list-create",
    ),

    path(
        "<int:pk>/",
        PlantDetailAPIView.as_view(),
        name="plant-detail",
    ),

]