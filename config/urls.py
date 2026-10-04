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
from accounts.views import (
    browser_login,
    browser_logout,
    signup,
    dashboard,
    plants_page,
    sanitizer_page,
    chloragel_page,
    admin_users_page,
    inspection_page,
    atp_page,
    records_search_page,
    daily_records_page,
    pdf_reports_page,
    audit_logs_page,
    corrective_actions_page,
)

urlpatterns = [
    path(
    "admin/users/",
    admin_users_page,
    name="admin-users",
    ),
    path("admin/", admin.site.urls),

    path("login/",browser_login,name="login"),
    path("logout/", browser_logout, name="logout"),

    path("titrations/sanitizer/",sanitizer_page,name="sanitizer-page"),
    path("titrations/chloragel/",chloragel_page,name="chloragel-page"),
    path("inspections/",inspection_page,name="inspection-page"),
    path("inspections/atp/",atp_page,name="atp-page"),
    path("records/search/",records_search_page,name="records-search-page"),
    path("records/daily/",daily_records_page,name="daily-records-page"),
    path("records/pdf/",pdf_reports_page,name="pdf-reports-page"),
    path("audit/",audit_logs_page,name="audit-logs-page"),
    path("corrective-actions/",corrective_actions_page,name="corrective-actions-page"),


    path("plants/",plants_page,name="plants-page"),

    path("signup/", signup, name="signup"),
    path("dashboard/", dashboard, name="dashboard"),

    path("api/auth/", include("accounts.api_urls")),
    path("api/plants/", include("plants.api_urls")),
    path("api/titrations/",include("titrations.api_urls")),
    path("api/inspections/",include("inspections.api_urls")),
    path("api/records/",include("records.api_urls")),
    path("api/corrective-actions/",include("corrective_actions.api_urls")),
    path("api/audit/",include("audit.api_urls")),
    path("api/titration-config/",include("titration_config.api_urls")),
    

]