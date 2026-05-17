from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.accounts.models import Profile, UserRole


@pytest.mark.django_db
def test_register_customer_creates_user_and_profile(client):
    url = reverse("accounts:register")
    payload = {
        "username": "buyer1",
        "email": "buyer1@example.com",
        "password1": "Str0ngPass!buyer",
        "password2": "Str0ngPass!buyer",
        "birth_date": "1990-01-15",
        "phone": "+375 (29) 123-45-67",
        "timezone": "Europe/Minsk",
        "address": "г. Минск",
    }
    response = client.post(url, payload, follow=False)
    assert response.status_code == 302

    User = get_user_model()
    user = User.objects.get(username="buyer1")
    assert user.role == UserRole.CUSTOMER
    assert hasattr(user, "profile")
    assert user.profile.phone == "+375 (29) 123-45-67"
    assert user.profile.timezone == "Europe/Minsk"


@pytest.mark.django_db
def test_admin_dashboard_forbidden_for_customer(client):
    User = get_user_model()
    user = User.objects.create_user(username="cust", email="c@example.com", password="pw12345678")
    user.role = UserRole.CUSTOMER
    user.save(update_fields=["role"])
    Profile.objects.create(
        user=user,
        birth_date=date(1990, 2, 2),
        phone="+375 (29) 222-33-44",
        address="addr",
    )
    assert client.login(username="cust", password="pw12345678") is True
    response = client.get(reverse("accounts:admin_dashboard"), follow=True)
    assert response.status_code == 403


@pytest.mark.django_db
def test_staff_dashboard_allowed_for_employee(client):
    User = get_user_model()
    user = User.objects.create_user(username="emp", email="e@example.com", password="pw12345678")
    user.role = UserRole.EMPLOYEE
    user.save(update_fields=["role"])
    Profile.objects.create(
        user=user,
        birth_date=date(1988, 3, 3),
        phone="+375 (29) 333-44-55",
        address="addr",
    )
    assert client.login(username="emp", password="pw12345678") is True
    response = client.get(reverse("accounts:staff_dashboard"), follow=True)
    assert response.status_code == 200
    assert "Панель" in response.content.decode()
