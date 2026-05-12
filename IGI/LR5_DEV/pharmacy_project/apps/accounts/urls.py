from django.urls import path

from apps.accounts import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.AccountLoginView.as_view(), name="login"),
    path("logout/", views.AccountLogoutView.as_view(), name="logout"),
    path("admin-dashboard/", views.AdminDashboardView.as_view(), name="admin_dashboard"),
    path("staff-dashboard/", views.StaffDashboardView.as_view(), name="staff_dashboard"),
]
