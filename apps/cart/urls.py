from django.urls import path

from apps.cart import views

app_name = "cart"

urlpatterns = [
    path("", views.CartDetailView.as_view(), name="detail"),
    path("add/<int:medication_id>/", views.cart_add, name="add"),
    path("change/<int:medication_id>/", views.cart_change, name="change"),
    path("quantity/<int:medication_id>/", views.cart_set_quantity, name="set_quantity"),
    path("remove/<int:medication_id>/", views.cart_remove, name="remove"),
    path("clear/", views.cart_clear, name="clear"),
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("checkout/success/", views.PaymentSuccessView.as_view(), name="success"),
]
