from django.urls import path

from .views import (
    SignupAPIView,
    LoginAPIView,
    MeAPIView,
)


urlpatterns = [
    path("signup/", SignupAPIView.as_view(), name="api-signup"),
    path("login/", LoginAPIView.as_view(), name="api-login"),
    path("me/", MeAPIView.as_view(), name="api-me"),
]