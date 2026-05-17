from django.urls import path

from .views import HealthAPIView, OpenFdaLabelLookupAPIView, RxNormLookupAPIView

app_name = "catalog"

urlpatterns = [
    path("health/", HealthAPIView.as_view(), name="health"),
    path("external/rxnorm/", RxNormLookupAPIView.as_view(), name="rxnorm_lookup"),
    path("external/openfda/", OpenFdaLabelLookupAPIView.as_view(), name="openfda_lookup"),
]
