from django.urls import path

from .views import (
    InspectionTemplateListCreateAPIView,
    InspectionSectionListCreateAPIView,
    InspectionQuestionListCreateAPIView,
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
]