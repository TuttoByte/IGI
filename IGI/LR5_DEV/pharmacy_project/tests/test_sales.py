from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse

from apps.accounts.models import Profile, UserRole
from apps.pharmacy.models import Category, Department, Medication
from apps.sales.models import Sale
from apps.sales.services import SaleLineInput, SaleService


@pytest.mark.django_db
def test_sale_list_staff_only(client):
    url = reverse("sales:sale_list")
    assert client.get(url).status_code == 302
    User = get_user_model()
    User.objects.create_user(username="u", email="u@e.com", password="pw", is_staff=False)
    client.login(username="u", password="pw")
    assert client.get(url).status_code == 403


@pytest.mark.django_db
def test_create_sale_decrements_stock(client):
    User = get_user_model()
    staff = User.objects.create_superuser(username="seller", email="s@e.com", password="pw12345678")
    cust = User.objects.create_user(
        username="buyer",
        email="b@e.com",
        password="pw12345678",
        role=UserRole.CUSTOMER,
    )
    Profile.objects.create(
        user=cust,
        birth_date=date(1992, 1, 1),
        phone="+375 (29) 444-55-66",
        address="x",
    )
    cat = Category.objects.create(name="C", slug="c")
    dep = Department.objects.create(name="D", slug="d", floor=1)
    med = Medication.objects.create(
        code="SALE-1",
        name="Med sale",
        slug="med-sale",
        description="",
        instruction="",
        manufacturer="m",
        price=Decimal("10.00"),
        quantity=5,
        expiration_date=date.today() + timedelta(days=30),
        category=cat,
        department=dep,
    )
    client.login(username="seller", password="pw12345678")
    url = reverse("sales:sale_create")
    payload = {
        "customer": str(cust.pk),
        "employee": str(staff.pk),
        "items-TOTAL_FORMS": "2",
        "items-INITIAL_FORMS": "0",
        "items-MIN_NUM_FORMS": "1",
        "items-MAX_NUM_FORMS": "1000",
        "items-0-medication": str(med.pk),
        "items-0-quantity": "2",
        "items-1-medication": "",
        "items-1-quantity": "",
    }
    r = client.post(url, payload)
    assert r.status_code == 302
    med.refresh_from_db()
    assert med.quantity == 3
    sale = Sale.objects.get()
    assert sale.total_price == Decimal("20.00")
    assert sale.items.count() == 1


@pytest.mark.django_db
def test_create_sale_insufficient_stock(client):
    User = get_user_model()
    staff = User.objects.create_superuser(username="seller2", email="s2@e.com", password="pw12345678")
    cust = User.objects.create_user(
        username="buyer2",
        email="b2@e.com",
        password="pw12345678",
        role=UserRole.CUSTOMER,
    )
    Profile.objects.create(
        user=cust,
        birth_date=date(1992, 1, 1),
        phone="+375 (29) 444-55-67",
        address="x",
    )
    cat = Category.objects.create(name="C2", slug="c2")
    dep = Department.objects.create(name="D2", slug="d2", floor=1)
    med = Medication.objects.create(
        code="SALE-2",
        name="Med sale 2",
        slug="med-sale-2",
        description="",
        instruction="",
        manufacturer="m",
        price=Decimal("1.00"),
        quantity=1,
        expiration_date=date.today() + timedelta(days=30),
        category=cat,
        department=dep,
    )
    client.login(username="seller2", password="pw12345678")
    url = reverse("sales:sale_create")
    payload = {
        "customer": str(cust.pk),
        "employee": str(staff.pk),
        "items-TOTAL_FORMS": "1",
        "items-INITIAL_FORMS": "0",
        "items-MIN_NUM_FORMS": "1",
        "items-MAX_NUM_FORMS": "1000",
        "items-0-medication": str(med.pk),
        "items-0-quantity": "5",
    }
    r = client.post(url, payload)
    assert r.status_code == 200
    assert Sale.objects.count() == 0
    med.refresh_from_db()
    assert med.quantity == 1


@pytest.mark.django_db
def test_sale_service_validation():
    User = get_user_model()
    staff = User.objects.create_superuser(username="s3", email="s3@e.com", password="pw12345678")
    cust = User.objects.create_user(username="b3", email="b3@e.com", password="pw12345678", role=UserRole.CUSTOMER)
    Profile.objects.create(
        user=cust,
        birth_date=date(1991, 1, 1),
        phone="+375 (29) 444-55-68",
        address="x",
    )
    cat = Category.objects.create(name="C3", slug="c3")
    dep = Department.objects.create(name="D3", slug="d3", floor=1)
    med = Medication.objects.create(
        code="SALE-3",
        name="Med 3",
        slug="med-3",
        description="",
        instruction="",
        manufacturer="m",
        price=Decimal("2.00"),
        quantity=1,
        expiration_date=date.today() + timedelta(days=30),
        category=cat,
        department=dep,
    )
    with pytest.raises(ValidationError):
        SaleService.create_completed_sale(
            customer_id=cust.pk,
            employee_id=staff.pk,
            lines=(SaleLineInput(medication_id=med.pk, quantity=99),),
        )
