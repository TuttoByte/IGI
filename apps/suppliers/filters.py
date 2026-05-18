"""
Фильтрация списка поставщиков (django-filter).

Поиск по названию — через icontains на name (индекс по name ускоряет сортировку;
для полнотекста на больших объёмах смотреть PostgreSQL pg_trgm / Elastic).
"""
from __future__ import annotations

import django_filters
from django.db.models import QuerySet

from apps.suppliers.models import Supplier


class SupplierFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search", label="Поиск по названию")
    ordering = django_filters.OrderingFilter(
        fields=(
            ("name", "по названию"),
            ("contract_number", "по договору"),
            ("email", "по email"),
            ("created_at", "по дате создания"),
        ),
        label="Сортировка",
    )

    class Meta:
        model = Supplier
        fields = ["email"]

    def filter_search(self, queryset: QuerySet[Supplier], name: str, value: str) -> QuerySet[Supplier]:
        del name
        if not value:
            return queryset
        return queryset.filter(name__icontains=value)
