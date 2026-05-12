from django.urls import path

from .views import HealthAPIView

app_name = "catalog"

urlpatterns = [
    path("health/", HealthAPIView.as_view(), name="health"),
]
