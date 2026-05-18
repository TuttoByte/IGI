"""URL-маршрутизация проекта pharmacy_project."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/sales/", include("apps.sales.urls")),
    path("dashboard/suppliers/", include("apps.suppliers.urls")),
    path("dashboard/analytics/", include("apps.analytics.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("cabinet/", include("apps.cabinet.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("api/", include("apps.catalog.urls")),
    path("pharmacy/", include("apps.pharmacy.urls")),
    path("reviews/", include("apps.reviews.urls")),
    path("", include("apps.core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
