"""Фильтры списка отзывов: модерация, препарат, сортировка (свежие / по оценке)."""
from __future__ import annotations

import django_filters

from apps.pharmacy.models import Medication
from apps.reviews.models import Review, ReviewModerationStatus


class ReviewFilter(django_filters.FilterSet):
    moderation_status = django_filters.ChoiceFilter(
        choices=ReviewModerationStatus.choices,
        label="Модерация",
    )
    medication = django_filters.ModelChoiceFilter(
        queryset=Medication.objects.order_by("name"),
        label="Препарат",
    )
    ordering = django_filters.OrderingFilter(
        fields=(
            ("-created_at", "сначала новые"),
            ("created_at", "сначала старые"),
            ("-rating", "сначала высокая оценка"),
            ("rating", "сначала низкая оценка"),
        ),
        label="Сортировка",
    )

    class Meta:
        model = Review
        fields = ["moderation_status", "medication"]
