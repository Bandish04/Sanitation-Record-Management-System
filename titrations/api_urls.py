from django.urls import path

from .views import (
    SanitizerTitrationListCreateAPIView,
    ChloragelTitrationListCreateAPIView,
)



urlpatterns = [
    path(
        "",
        SanitizerTitrationListCreateAPIView.as_view(),
        name="sanitizer-titration-list-create",
    ),
    path(
        "chloragel/",
        ChloragelTitrationListCreateAPIView.as_view(),
        name="chloragel-titration-list-create",
    ),
]