
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from accounts.views import (
    browser_login,
    browser_logout,
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
      # Admin user management
    path("admin/users/", admin_users_page, name="admin-users"),
    # Django Admin
    path("admin/", admin.site.urls),

    # Home and authentication
    path(
        "",
        RedirectView.as_view(url="/login/", permanent=False),
        name="home",
    ),
    path("login/", browser_login, name="login"),
    path("logout/", browser_logout, name="logout"),

  

    # Application pages
    path("dashboard/", dashboard, name="dashboard"),
    path("plants/", plants_page, name="plants-page"),
    path(
        "titrations/sanitizer/",
        sanitizer_page,
        name="sanitizer-page",
    ),
    path(
        "titrations/chloragel/",
        chloragel_page,
        name="chloragel-page",
    ),
    path("inspections/", inspection_page, name="inspection-page"),
    path("inspections/atp/", atp_page, name="atp-page"),
    path("records/search/", records_search_page, name="records-search-page"),
    path("records/daily/", daily_records_page, name="daily-records-page"),
    path("records/pdf/", pdf_reports_page, name="pdf-reports-page"),
    path("audit/", audit_logs_page, name="audit-logs-page"),
    path(
        "corrective-actions/",
        corrective_actions_page,
        name="corrective-actions-page",
    ),

    # Existing APIs
    path("api/auth/", include("accounts.api_urls")),
    path("api/plants/", include("plants.api_urls")),
    path("api/titrations/", include("titrations.api_urls")),
    path("api/inspections/", include("inspections.api_urls")),
    path("api/records/", include("records.api_urls")),
    path(
        "api/corrective-actions/",
        include("corrective_actions.api_urls"),
    ),
    path("api/audit/", include("audit.api_urls")),
    path(
        "api/titration-config/",
        include("titration_config.api_urls"),
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
