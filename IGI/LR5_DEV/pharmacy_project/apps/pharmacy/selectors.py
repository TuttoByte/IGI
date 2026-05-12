"""
Слой чтения: готовые QuerySet-ы с select_related / prefetch_related.

Представления и DRF-viewset'ы не собирают цепочки ORM вручную — так проще
подменять реализацию (кэш, read-replica) и избегать N+1.
"""
from __future__ import annotations

from django.db.models import Prefetch, QuerySet

from apps.pharmacy.models import Category, Department, Medication


def medications_for_catalog() -> QuerySet[Medication]:
    """Каталог: FK-справочники подтягиваются одним JOIN на строку препарата."""
    return Medication.objects.select_related("category", "department").order_by("name")


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
                queryset=Medication.objects.select_related("department").order_by("name"),
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
                queryset=Medication.objects.select_related("category").order_by("name"),
            )
        )
    )
    return qs.first()
