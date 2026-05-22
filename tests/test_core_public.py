from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.core.models import EmployeeContact, NewsArticle


@pytest.mark.django_db
def test_news_list_and_detail_render_required_image(client):
    article = NewsArticle.objects.create(
        title="Поступление сезонных товаров",
        slug="postuplenie-sezonnyh-tovarov",
        image="news/season.jpg",
        lead="В каталоге появились сезонные позиции.",
        content="Проверьте наличие в удобном отделе аптеки.",
        published_at=timezone.now() - timedelta(hours=1),
    )
    NewsArticle.objects.create(
        title="Черновик",
        slug="chernovik",
        image="news/draft.jpg",
        lead="Не показывается",
        content="Не опубликовано",
        is_published=False,
    )

    list_response = client.get(reverse("core:news_list"))
    body = list_response.content.decode()
    assert list_response.status_code == 200
    assert article.title in body
    assert article.image.url in body
    assert "Черновик" not in body

    detail_response = client.get(article.get_absolute_url())
    detail_body = detail_response.content.decode()
    assert detail_response.status_code == 200
    assert article.lead in detail_body
    assert article.image.url in detail_body

    hidden_response = client.get(reverse("core:news_detail", kwargs={"slug": "chernovik"}))
    assert hidden_response.status_code == 404


@pytest.mark.django_db
def test_contacts_render_employee_photo_fio_and_text_calendar(client):
    employee = EmployeeContact.objects.create(
        full_name="Иванова Мария Сергеевна",
        slug="ivanova-mariya-sergeevna-test",
        position="Заведующая аптекой",
        photo="employees/ivanova.jpg",
        phone="+375 (29) 700-10-01",
        email="manager@example.local",
        work_calendar="Пн-Пт: 09:00-17:00\nСб: консультации по записи\nВс: выходной",
        note="Отвечает за работу торгового зала.",
    )

    response = client.get(reverse("core:contacts"))
    body = response.content.decode()
    assert response.status_code == 200
    assert employee.full_name in body
    assert employee.position in body
    assert employee.photo.url in body
    assert "Пн-Пт: 09:00-17:00" in body
    assert "консультации по записи" in body
