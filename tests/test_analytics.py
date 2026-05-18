import pytest
from django.urls import reverse

from apps.accounts.models import UserRole
from apps.analytics import selectors as analytics_selectors


@pytest.mark.django_db
def test_analytics_dashboard_requires_staff(client):
    url = reverse("analytics:dashboard")
    assert client.get(url).status_code == 302
    from django.contrib.auth import get_user_model

    User = get_user_model()
    u = User.objects.create_user(username="cust", email="c@e.com", password="pw12345678", is_staff=False)
    u.role = UserRole.CUSTOMER
    u.save(update_fields=["role"])
    client.login(username="cust", password="pw12345678")
    assert client.get(url).status_code == 403


@pytest.mark.django_db
def test_analytics_selectors_with_completed_sales():
    from datetime import date, timedelta
    from decimal import Decimal

    from django.contrib.auth import get_user_model

    from apps.accounts.models import Profile, UserRole
    from apps.pharmacy.models import Category, Department, Medication
    from apps.sales.models import Sale, SaleItem, SaleStatus

    User = get_user_model()
    staff = User.objects.create_superuser(username="an-staff", email="a@e.com", password="pw12345678")
    cust = User.objects.create_user(username="an-cust", email="c@e.com", password="pw12345678", role=UserRole.CUSTOMER)
    Profile.objects.create(
        user=cust,
        birth_date=date(1990, 1, 1),
        phone="+375 (29) 900-11-22",
        address="x",
    )
    cat = Category.objects.create(name="AC", slug="ac-an")
    dep = Department.objects.create(name="Отдел А", slug="dep-an-a", floor=1)
    med = Medication.objects.create(
        code="AN-1",
        name="Популярный",
        slug="an-pop",
        description="",
        instruction="",
        manufacturer="m",
        price=Decimal("5.00"),
        quantity=100,
        expiration_date=date.today() + timedelta(days=60),
        category=cat,
        department=dep,
    )
    sale = Sale.objects.create(
        customer=cust,
        employee=staff,
        status=SaleStatus.COMPLETED,
        total_price=Decimal("30.00"),
    )
    SaleItem.objects.create(sale=sale, medication=med, quantity=6, price=Decimal("5.00"), subtotal=Decimal("30.00"))

    summary = analytics_selectors.pharmacy_analytics_summary()
    assert summary.total_revenue == Decimal("30.00")
    assert summary.completed_sales_count == 1
    assert summary.average_check == Decimal("30.00")

    dept_rows = analytics_selectors.pharmacy_revenue_by_department()
    assert len(dept_rows) == 1
    assert dept_rows[0].revenue == Decimal("30.00")
    assert dept_rows[0].line_count == 1

    popular = analytics_selectors.pharmacy_popular_medications(limit=5)
    assert len(popular) == 1
    assert popular[0].units_sold == 6
    assert popular[0].revenue == Decimal("30.00")

    by_day = analytics_selectors.pharmacy_sales_by_day(days=7)
    assert len(by_day) >= 1
    payload = analytics_selectors.chart_payload_by_day(by_day)
    assert "labels" in payload and "revenue" in payload


@pytest.mark.django_db
def test_analytics_dashboard_ok_for_staff(client):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    User.objects.create_superuser(username="dash-admin", email="d@e.com", password="pw12345678")
    client.login(username="dash-admin", password="pw12345678")
    r = client.get(reverse("analytics:dashboard"))
    assert r.status_code == 200
    body = r.content.decode()
    assert "Дашборд" in body
    assert "<script" not in body
    assert "<canvas" not in body
