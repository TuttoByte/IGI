import pytest
from django.urls import reverse

from apps.pharmacy.external_apis import ExternalApiRecord, ExternalApiResult


@pytest.mark.django_db
def test_api_health(client):
    url = reverse("catalog:health")
    response = client.get(url)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.django_db
def test_external_rxnorm_api_uses_server_lookup(client, monkeypatch):
    def fake_lookup(query):
        return ExternalApiResult(
            source="RxNorm / RxNav",
            query=query,
            status="Данные получены.",
            records=(ExternalApiRecord(title="Aspirin", facts=(("RxCUI", "1191"),)),),
        )

    monkeypatch.setattr("apps.catalog.views.lookup_rxnorm", fake_lookup)
    response = client.get(reverse("catalog:rxnorm_lookup"), {"q": "aspirin"})
    assert response.status_code == 200
    assert response.json()["records"][0]["title"] == "Aspirin"


@pytest.mark.django_db
def test_external_openfda_api_uses_server_lookup(client, monkeypatch):
    def fake_lookup(query):
        return ExternalApiResult(
            source="openFDA Drug Label",
            query=query,
            status="Данные получены.",
            records=(ExternalApiRecord(title="Aspirin", facts=(("NDC", "0000"),)),),
        )

    monkeypatch.setattr("apps.catalog.views.lookup_openfda_label", fake_lookup)
    response = client.get(reverse("catalog:openfda_lookup"), {"q": "aspirin"})
    assert response.status_code == 200
    assert response.json()["source"] == "openFDA Drug Label"
