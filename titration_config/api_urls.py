from django.urls import path

from .views import (
    TitrationLimitListCreateAPIView,
    TitrationLimitDetailAPIView,
)


urlpatterns = [
    path(
        "",
        TitrationLimitListCreateAPIView.as_view(),
        name="titration-limit-list-create",
    ),
    path(
        "<int:pk>/",
        TitrationLimitDetailAPIView.as_view(),
        name="titration-limit-detail",
    ),
]   