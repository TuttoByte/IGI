import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_api_health(client):
    url = reverse("catalog:health")
    response = client.get(url)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
