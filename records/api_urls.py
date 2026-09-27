from django.urls import path

from .views import (
    CombinedRecordsAPIView,
    DailyRecordsAPIView,
)


urlpatterns = [
    path(
        "",
        CombinedRecordsAPIView.as_view(),
        name="combined-records",
    ),
    path(
        "daily/",
        DailyRecordsAPIView.as_view(),
        name="daily-records",
    ),
]