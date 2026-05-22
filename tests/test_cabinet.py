import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.accounts.models import Profile, UserRole


@pytest.mark.django_db
def test_cabinet_for_customer_shows_birth_date_text_calendar():
    from datetime import date
    from django.test import Client

    User = get_user_model()
    cust = User.objects.create_user(username="cab_c", email="cc@e.com", password="pw12345678")
    cust.role = UserRole.CUSTOMER
    cust.save(update_fields=["role"])
    Profile.objects.create(
        user=cust,
        birth_date=date(1990, 1, 1),
        phone="+375 (29) 777-88-99",
        address="x",
    )
    c = Client()
    assert c.login(username="cab_c", password="pw12345678") is True
    r = c.get(reverse("frontend:home"))
    body = r.content.decode()
    assert r.status_code == 200
    assert "Личный кабинет" in body
    assert "01.01.1990" in body
    assert "Январь 1990" in body
    assert "[01]" in body


@pytest.mark.django_db
def test_cabinet_available_for_staff_and_user_without_profile(client):
    User = get_user_model()
    staff = User.objects.create_user(
        username="cab_staff",
        email="staff@e.com",
        password="pw12345678",
        role=UserRole.EMPLOYEE,
    )

    assert client.login(username=staff.username, password="pw12345678") is True
    response = client.get(reverse("frontend:home"))
    body = response.content.decode()
    assert response.status_code == 200
    assert "Расширенный профиль пока не заполнен" in body
    assert "Дата рождения не указана" in body
    assert reverse("dashboard:index") in body
