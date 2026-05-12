from django.urls import path

from apps.suppliers import views

app_name = "suppliers"

urlpatterns = [
    path("", views.SupplierListView.as_view(), name="supplier_list"),
    path("new/", views.SupplierCreateView.as_view(), name="supplier_create"),
    path("<slug:slug>/", views.SupplierDetailView.as_view(), name="supplier_detail"),
    path("<slug:slug>/edit/", views.SupplierUpdateView.as_view(), name="supplier_update"),
    path("<slug:slug>/delete/", views.SupplierDeleteView.as_view(), name="supplier_delete"),
]
