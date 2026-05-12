from django.urls import path

from apps.reviews import views

app_name = "reviews"

urlpatterns = [
    path("", views.ReviewListView.as_view(), name="review_list"),
    path("<int:pk>/", views.ReviewDetailView.as_view(), name="review_detail"),
    path("create/<slug:medication_slug>/", views.ReviewCreateView.as_view(), name="review_create"),
    path("<int:pk>/edit/", views.ReviewUpdateView.as_view(), name="review_update"),
    path("<int:pk>/delete/", views.ReviewDeleteView.as_view(), name="review_delete"),
]
