from django.urls import path

from apps.cabinet import views

app_name = "frontend"

urlpatterns = [
    path("", views.CabinetHomeView.as_view(), name="home"),
]
