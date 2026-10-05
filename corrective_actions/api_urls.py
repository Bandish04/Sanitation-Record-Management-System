from django.urls import path

from .views import (
    CorrectiveActionListCreateAPIView,
    CorrectiveActionDetailAPIView,
    CorrectiveActionOptionsAPIView,
)


urlpatterns = [
    path(
        "",
        CorrectiveActionListCreateAPIView.as_view(),
        name="corrective-action-list-create",
    ),
    path(
        "options/",
        CorrectiveActionOptionsAPIView.as_view(),
        name="corrective-action-options",
    ),
    path(
        "<int:pk>/",
        CorrectiveActionDetailAPIView.as_view(),
        name="corrective-action-detail",
    ),
]