import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse


@pytest.mark.django_db
def test_supplier_list_redirects_anonymous(client):
    url = reverse("suppliers:supplier_list")
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_supplier_list_forbidden_for_non_staff(client):
    User = get_user_model()
    User.objects.create_user(username="cust", email="c@e.com", password="pw12345678", is_staff=False)
    client.login(username="cust", password="pw12345678")
    response = client.get(reverse("suppliers:supplier_list"))
    assert response.status_code == 403


@pytest.mark.django_db
def test_supplier_list_ok_for_staff(client):
    User = get_user_model()
    User.objects.create_superuser(username="staffer", email="st@e.com", password="pw12345678")
    client.login(username="staffer", password="pw12345678")
    response = client.get(reverse("suppliers:supplier_list"))
    assert response.status_code == 200
