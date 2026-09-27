from django.urls import path

from .views import CorrectiveActionListCreateAPIView


urlpatterns = [
    path(
        "",
        CorrectiveActionListCreateAPIView.as_view(),
        name="corrective-action-list-create",
    ),
]