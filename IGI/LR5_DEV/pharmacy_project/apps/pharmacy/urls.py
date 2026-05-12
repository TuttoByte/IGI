from django.urls import path

from apps.pharmacy import views

app_name = "pharmacy"

urlpatterns = [
    path("medications/", views.MedicationListView.as_view(), name="medication_list"),
    path("medications/<slug:slug>/", views.MedicationDetailView.as_view(), name="medication_detail"),
    path("categories/<slug:slug>/", views.CategoryDetailView.as_view(), name="category_detail"),
    path("departments/<slug:slug>/", views.DepartmentDetailView.as_view(), name="department_detail"),
]
