"""
Чтение: заранее собранные QuerySet-ы.

Как оптимизировать запросы:
- для списка поставщиков — annotate(Count('medications')) одним запросом вместо
  per-row COUNT в шаблоне;
- для карточки поставщика — prefetch_related('medications') + select_related на FK
  препарата (category, department), чтобы не было N+1 при отрисовке списка SKU.
"""
from __future__ import annotations

from django.db.models import Count, Prefetch, QuerySet

from apps.pharmacy.models import Medication
from apps.suppliers.models import Supplier


def suppliers_for_list() -> QuerySet[Supplier]:
    return (
        Supplier.objects.all()
        .annotate(medication_count=Count("medications", distinct=True))
        .order_by("name")
    )


def supplier_by_slug_with_medications(slug: str) -> Supplier | None:
    med_qs = Medication.objects.select_related("category", "department").order_by("name")
    return (
        Supplier.objects.filter(slug=slug)
        .prefetch_related(Prefetch("medications", queryset=med_qs))
        .first()
    )


def supplier_queryset_for_crud() -> QuerySet[Supplier]:
    """Базовый queryset для форм (ordering, без лишних JOIN)."""
    return Supplier.objects.all().order_by("name")
