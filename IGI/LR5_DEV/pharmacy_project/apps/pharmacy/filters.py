"""
django-filter: поиск, сортировка и фильтры для каталога препаратов.

FilterSet переиспользуется во view (FilterView) и при необходимости в DRF
(GenericAPIView + filterset_class) без дублирования условий.
"""
from __future__ import annotations

import django_filters
from django.db.models import Q, QuerySet

from apps.pharmacy.models import Medication


class MedicationFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search", label="Поиск")

    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte", label="Цена от")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte", label="Цена до")

    expiration_after = django_filters.DateFilter(
        field_name="expiration_date",
        lookup_expr="gte",
        label="Годен с",
    )
    expiration_before = django_filters.DateFilter(
        field_name="expiration_date",
        lookup_expr="lte",
        label="Годен до",
    )

    ordering = django_filters.OrderingFilter(
        fields=(
            ("name", "по названию"),
            ("price", "по цене"),
            ("expiration_date", "по сроку годности"),
            ("quantity", "по остатку"),
            ("code", "по коду"),
            ("created_at", "по дате добавления"),
            ("avg_review_rating", "по рейтингу"),
        ),
        label="Сортировка",
    )

    class Meta:
        model = Medication
        fields = ["category", "department", "requires_prescription"]

    def filter_search(self, queryset: QuerySet[Medication], name: str, value: str) -> QuerySet[Medication]:
        del name
        if not value:
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
            | Q(code__icontains=value)
            | Q(description__icontains=value)
            | Q(instruction__icontains=value)
            | Q(manufacturer__icontains=value)
        )
