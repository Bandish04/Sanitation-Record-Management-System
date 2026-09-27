from django.urls import path

from .views import AuditLogListAPIView


urlpatterns = [
    path(
        "",
        AuditLogListAPIView.as_view(),
        name="audit-list",
    ),
]