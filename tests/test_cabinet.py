import pytest
from django.urls import reverse

from apps.accounts.models import Profile, UserRole


@pytest.mark.django_db
def test_cabinet_customer_only():
    from datetime import date
    from django.contrib.auth import get_user_model
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
    assert r.status_code == 200

    staff = User.objects.create_superuser(username="cab_a", email="ca@e.com", password="pw12345678")
    c2 = Client()
    c2.login(username="cab_a", password="pw12345678")
    r2 = c2.get(reverse("frontend:home"))
    assert r2.status_code == 403
