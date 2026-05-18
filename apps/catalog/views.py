from dataclasses import asdict

from rest_framework.response import Response
from rest_framework.views import APIView

from apps.pharmacy.external_apis import lookup_openfda_label, lookup_rxnorm


class HealthAPIView(APIView):
    """Проверка доступности API (DRF)."""

    def get(self, request):
        return Response({"status": "ok"})


class RxNormLookupAPIView(APIView):
    """Поиск препарата в открытом справочнике RxNorm/RxNav."""

    def get(self, request):
        result = lookup_rxnorm(request.query_params.get("q", ""))
        return Response(asdict(result))


class OpenFdaLabelLookupAPIView(APIView):
    """Поиск препарата в открытом справочнике openFDA drug label."""

    def get(self, request):
        result = lookup_openfda_label(request.query_params.get("q", ""))
        return Response(asdict(result))
