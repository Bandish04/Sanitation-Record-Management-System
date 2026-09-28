from django.urls import path

from .views import (
    InspectionTemplateListCreateAPIView,
    InspectionSectionListCreateAPIView,
    InspectionQuestionListCreateAPIView,
    SanitationInspectionListCreateAPIView,
    SanitationInspectionDetailAPIView,
    InspectionAnswerCreateAPIView,
    InspectionAnswerDetailAPIView,
    SanitationInspectionSubmitAPIView,
    SanitationInspectionCorrectionAPIView,
    ATPReportListCreateAPIView,
)

urlpatterns = [
    path(
        "templates/",
        InspectionTemplateListCreateAPIView.as_view(),
        name="inspection-template-list-create",
    ),

    path(
        "sections/",
        InspectionSectionListCreateAPIView.as_view(),
        name="inspection-section-list-create",
    ),

    path(
        "questions/",
        InspectionQuestionListCreateAPIView.as_view(),
        name="inspection-question-list-create",
    ),

    path(
        "",
        SanitationInspectionListCreateAPIView.as_view(),
        name="inspection-list-create",
    ),

    path(
        "<int:pk>/",
        SanitationInspectionDetailAPIView.as_view(),
        name="inspection-detail",
    ),

    path(
        "<int:pk>/submit/",
        SanitationInspectionSubmitAPIView.as_view(),
        name="inspection-submit",
    ),

    path(
        "<int:pk>/correct/",
        SanitationInspectionCorrectionAPIView.as_view(),
        name="inspection-correct",
    ),

    path(
        "answers/",
        InspectionAnswerCreateAPIView.as_view(),
        name="inspection-answer-create",
    ),

    path(
        "answers/<int:pk>/",
        InspectionAnswerDetailAPIView.as_view(),
        name="inspection-answer-detail",
    ),

    path(
        "atp/",
        ATPReportListCreateAPIView.as_view(),
        name="atp-list-create",
    ),
]