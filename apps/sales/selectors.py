"""Селекторы чтения для продаж (единая точка prefetch / select_related)."""
from __future__ import annotations

from django.db.models import Prefetch, QuerySet

from apps.sales.models import Sale, SaleItem


def sales_for_list() -> QuerySet[Sale]:
    return Sale.objects.select_related("customer", "employee").order_by("-created_at")


def sale_by_pk_with_items(pk: int) -> Sale | None:
    item_qs = SaleItem.objects.select_related("medication").order_by("pk")
    return (
        Sale.objects.filter(pk=pk)
        .select_related("customer", "employee")
        .prefetch_related(Prefetch("items", queryset=item_qs))
        .first()
    )
