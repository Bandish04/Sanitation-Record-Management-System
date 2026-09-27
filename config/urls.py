"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

from accounts.views import signup, dashboard


urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html"
        ),
        name="login",
    ),

    path("signup/", signup, name="signup"),
    path("dashboard/", dashboard, name="dashboard"),

    path("api/auth/", include("accounts.api_urls")),
    path("api/plants/", include("plants.api_urls")),
    path("api/titrations/",include("titrations.api_urls")),
    path("api/inspections/",include("inspections.api_urls")),
    path("api/records/",include("records.api_urls")),
    path("api/corrective-actions/",include("corrective_actions.api_urls")),
    path("api/audit/",include("audit.api_urls")),

]