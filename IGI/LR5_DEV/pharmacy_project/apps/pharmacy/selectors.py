"""
Слой чтения: готовые QuerySet-ы с select_related / prefetch_related.

Представления и DRF-viewset'ы не собирают цепочки ORM вручную — так проще
подменять реализацию (кэш, read-replica) и избегать N+1.
"""
from __future__ import annotations

from django.db.models import Avg, Count, Prefetch, Q, QuerySet, Value
from django.db.models.fields import DecimalField
from django.db.models.functions import Coalesce

from apps.pharmacy.models import Category, Department, Medication
from apps.reviews.models import ReviewModerationStatus


def medications_for_catalog() -> QuerySet[Medication]:
    """
    Каталог: FK-справочники подтягиваются одним JOIN на строку препарата.

    prefetch_related('suppliers') — чтобы в шаблонах/списках не было N+1 при
    обращении к поставщикам (отдельная M2M-таблица).

    annotate(avg_review_rating, approved_reviews_count) — средняя оценка и число
    опубликованных отзывов одним запросом (без подгрузки всех Review в Python).
    """
    approved = Q(reviews__moderation_status=ReviewModerationStatus.APPROVED)
    return (
        Medication.objects.select_related("category", "department")
        .prefetch_related("suppliers")
        .annotate(
            avg_review_rating=Coalesce(
                Avg("reviews__rating", filter=approved),
                Value(0),
                output_field=DecimalField(max_digits=5, decimal_places=2),
            ),
            approved_reviews_count=Count("reviews", filter=approved),
        )
        .order_by("name")
    )


def medication_by_slug(slug: str) -> Medication | None:
    return medications_for_catalog().filter(slug=slug).first()


def categories_for_nav() -> QuerySet[Category]:
    return Category.objects.all().order_by("name")


def departments_for_nav() -> QuerySet[Department]:
    return Department.objects.all().order_by("floor", "name")


def category_detail_with_medications(slug: str) -> Category | None:
    """
    Карточка категории: обратная связь O2M через prefetch — без N+1 по препаратам.
    """
    qs = (
        Category.objects.filter(slug=slug)
        .prefetch_related(
            Prefetch(
                "medications",
                queryset=Medication.objects.select_related("department")
                .prefetch_related("suppliers")
                .order_by("name"),
            )
        )
    )
    return qs.first()


def department_detail_with_medications(slug: str) -> Department | None:
    qs = (
        Department.objects.filter(slug=slug)
        .prefetch_related(
            Prefetch(
                "medications",
                queryset=Medication.objects.select_related("category")
                .prefetch_related("suppliers")
                .order_by("name"),
            )
        )
    )
    return qs.first()
