from django.urls import path

from .views import (
    CorrectiveActionListCreateAPIView,
    CorrectiveActionDetailAPIView,
)


urlpatterns = [
    path(
        "",
        CorrectiveActionListCreateAPIView.as_view(),
        name="corrective-action-list-create",
    ),
    path(
        "<int:pk>/",
        CorrectiveActionDetailAPIView.as_view(),
        name="corrective-action-detail",
    ),
]