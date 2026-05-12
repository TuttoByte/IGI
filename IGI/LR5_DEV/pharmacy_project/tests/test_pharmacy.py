from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.urls import reverse

from apps.pharmacy.models import Category, Department, Medication
from apps.pharmacy.services import MedicationInventoryService


@pytest.mark.django_db
def test_medication_list_search_and_ordering(client):
    cat = Category.objects.create(name="Обезболивающие", slug="pain")
    dep = Department.objects.create(name="Зал А", slug="hall-a", floor=2)
    Medication.objects.create(
        code="ASP-1",
        name="Аспирин таблетки",
        slug="aspirin-tab",
        description="Классика",
        instruction="По назначению врача",
        manufacturer="ОАО Фарм",
        price=Decimal("15.00"),
        quantity=50,
        expiration_date=date.today() + timedelta(days=400),
        category=cat,
        department=dep,
    )
    Medication.objects.create(
        code="PAR-1",
        name="Парацетамол",
        slug="paracetamol",
        description="Дешёвый жаропонижающий",
        instruction="",
        manufacturer="ОАО Фарм",
        price=Decimal("5.00"),
        quantity=200,
        expiration_date=date.today() + timedelta(days=200),
        category=cat,
        department=dep,
    )

    url = reverse("pharmacy:medication_list")
    r = client.get(url, {"search": "Аспирин"})
    assert r.status_code == 200
    assert "Аспирин" in r.content.decode()
    assert "Парацетамол" not in r.content.decode()

    r2 = client.get(url, {"ordering": "price"})
    assert r2.status_code == 200


@pytest.mark.django_db
def test_inventory_service_apply_delta():
    cat = Category.objects.create(name="Витамины", slug="vit")
    dep = Department.objects.create(name="Зал Б", slug="hall-b", floor=1)
    m = Medication.objects.create(
        code="VIT-C",
        name="Витамин C",
        slug="vit-c",
        description="",
        instruction="",
        manufacturer="Импорт",
        price=Decimal("20.00"),
        quantity=10,
        expiration_date=date.today() + timedelta(days=100),
        category=cat,
        department=dep,
    )
    MedicationInventoryService.apply_stock_delta(m.pk, -3)
    m.refresh_from_db()
    assert m.quantity == 7
