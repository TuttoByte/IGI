from django.urls import include, path

from apps.dashboard import views

app_name = "dashboard"

urlpatterns = [
    path("", views.DashboardIndexView.as_view(), name="index"),
]
