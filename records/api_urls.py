from django.urls import path
from .pdf_views import DailyRecordsPDFAPIView

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
    path(
    "daily/pdf/",
    DailyRecordsPDFAPIView.as_view(),
    name="daily-records-pdf",
),
]