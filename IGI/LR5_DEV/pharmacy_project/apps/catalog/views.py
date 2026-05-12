from rest_framework.response import Response
from rest_framework.views import APIView


class HealthAPIView(APIView):
    """Проверка доступности API (DRF)."""

    def get(self, request):
        return Response({"status": "ok"})
