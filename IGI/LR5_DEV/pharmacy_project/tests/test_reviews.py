from datetime import date, timedelta
from decimal import Decimal
import uuid

import pytest
from django.urls import reverse

from apps.accounts.models import Profile, UserRole
from apps.pharmacy.models import Category, Department, Medication
from apps.reviews.models import Review, ReviewModerationStatus


def _med(slug: str | None = None, name: str = "Тестовый препарат") -> Medication:
    uid = uuid.uuid4().hex[:8]
    slug = slug or f"med-{uid}"
    cat = Category.objects.create(name=f"Кат-{uid}", slug=f"cat-{uid}")
    dep = Department.objects.create(name=f"Отдел-{uid}", slug=f"dep-{uid}", floor=1)
    return Medication.objects.create(
        code=f"TST-{uid}",
        name=name,
        slug=slug,
        description="",
        instruction="",
        manufacturer="Фарм",
        price=Decimal("10.00"),
        quantity=10,
        expiration_date=date.today() + timedelta(days=100),
        category=cat,
        department=dep,
    )


@pytest.mark.django_db
def test_review_create_requires_login(client):
    med = _med(slug="login-med-slug")
    url = reverse("reviews:review_create", kwargs={"medication_slug": med.slug})
    r = client.get(url)
    assert r.status_code == 302
    assert "login" in r.url.lower()


@pytest.mark.django_db
def test_review_create_and_duplicate(client):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.create_user(username="revuser", email="r@example.com", password="pw12345678")
    user.role = UserRole.CUSTOMER
    user.save(update_fields=["role"])
    Profile.objects.create(
        user=user,
        birth_date=date(1991, 1, 1),
        phone="+375 (29) 111-22-33",
        address="addr",
    )
    med = _med(slug="dup-med-slug")
    assert client.login(username="revuser", password="pw12345678") is True

    create_url = reverse("reviews:review_create", kwargs={"medication_slug": med.slug})
    r = client.post(create_url, {"rating": 5, "text": "Отлично"}, follow=False)
    assert r.status_code == 302
    assert Review.objects.filter(user=user, medication=med).count() == 1

    r2 = client.post(create_url, {"rating": 3, "text": "Ещё раз"}, follow=False)
    assert r2.status_code == 200
    assert "уже оставляли" in r2.content.decode().lower()


@pytest.mark.django_db
def test_anonymous_sees_only_approved_on_list(client):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    u = User.objects.create_user(username="author", email="a@example.com", password="pw12345678")
    Profile.objects.create(
        user=u,
        birth_date=date(1990, 1, 1),
        phone="+375 (29) 000-11-22",
        address="a",
    )
    med = _med(name="Мед А", slug="anon-med-a")
    Review.objects.create(
        user=u,
        medication=med,
        rating=4,
        text="ТЕКСТ_ТОЛЬКО_В_PENDING",
        moderation_status=ReviewModerationStatus.PENDING,
    )
    Review.objects.create(
        user=u,
        medication=_med(name="Мед Б"),
        rating=5,
        text="Ок",
        moderation_status=ReviewModerationStatus.APPROVED,
    )

    r = client.get(reverse("reviews:review_list"))
    assert r.status_code == 200
    body = r.content.decode()
    assert "Ок" in body
    assert "ТЕКСТ_ТОЛЬКО_В_PENDING" not in body


@pytest.mark.django_db
def test_medication_list_order_by_avg_rating(client):
    cat = Category.objects.create(name="К", slug="c-avg")
    dep = Department.objects.create(name="Д", slug="d-avg", floor=1)
    low = Medication.objects.create(
        code="LOW",
        name="Низкий рейтинг",
        slug="low-r",
        description="",
        instruction="",
        manufacturer="Ф",
        price=Decimal("1"),
        quantity=1,
        expiration_date=date.today() + timedelta(days=50),
        category=cat,
        department=dep,
    )
    high = Medication.objects.create(
        code="HI",
        name="Высокий рейтинг",
        slug="hi-r",
        description="",
        instruction="",
        manufacturer="Ф",
        price=Decimal("2"),
        quantity=2,
        expiration_date=date.today() + timedelta(days=50),
        category=cat,
        department=dep,
    )
    from django.contrib.auth import get_user_model

    User = get_user_model()
    for i, med in enumerate([low, high]):
        u = User.objects.create_user(username=f"u{i}", email=f"u{i}@e.com", password="pw12345678")
        Profile.objects.create(
            user=u,
            birth_date=date(1990, 1, 1),
            phone="+375 (29) 100-00-0" + str(i),
            address="x",
        )
        Review.objects.create(
            user=u,
            medication=med,
            rating=2 if med.slug == "low-r" else 5,
            text="",
            moderation_status=ReviewModerationStatus.APPROVED,
        )

    url = reverse("pharmacy:medication_list")
    r = client.get(url, {"ordering": "-по рейтингу"})
    assert r.status_code == 200
    text = r.content.decode()
    pos_hi = text.find("Высокий рейтинг")
    pos_lo = text.find("Низкий рейтинг")
    assert pos_hi != -1 and pos_lo != -1, text[:4000]
    assert pos_hi < pos_lo
