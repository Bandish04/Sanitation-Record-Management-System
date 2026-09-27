from django.urls import path

from .views import (
    SanitizerTitrationListCreateAPIView,
    SanitizerTitrationDetailAPIView,
    SanitizerTitrationSubmitAPIView,
    ChloragelTitrationListCreateAPIView,
    ChloragelTitrationDetailAPIView,
    ChloragelTitrationSubmitAPIView,
)


urlpatterns = [

    # ========================================================
    # SANITIZER TITRATION
    # ========================================================

    path(
        "",
        SanitizerTitrationListCreateAPIView.as_view(),
        name="sanitizer-titration-list-create",
    ),

    path(
        "<int:pk>/",
        SanitizerTitrationDetailAPIView.as_view(),
        name="sanitizer-titration-detail",
    ),

    path(
        "<int:pk>/submit/",
        SanitizerTitrationSubmitAPIView.as_view(),
        name="sanitizer-titration-submit",
    ),

    # ========================================================
    # CHLORAGEL TITRATION
    # ========================================================

    path(
        "chloragel/",
        ChloragelTitrationListCreateAPIView.as_view(),
        name="chloragel-titration-list-create",
    ),

    path(
        "chloragel/<int:pk>/",
        ChloragelTitrationDetailAPIView.as_view(),
        name="chloragel-titration-detail",
    ),

    path(
        "chloragel/<int:pk>/submit/",
        ChloragelTitrationSubmitAPIView.as_view(),
        name="chloragel-titration-submit",
    ),
]