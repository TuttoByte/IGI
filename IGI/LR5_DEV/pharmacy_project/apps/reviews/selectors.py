"""
Чтение отзывов и агрегатов.

Как избежать N+1:
- для списков отзывов всегда используйте select_related("user", "medication") —
  иначе шаблон с {{ review.user.username }} и {{ review.medication.name }} даст
  отдельный SQL на каждую строку;
- средний рейтинг и количество для одного препарата — один aggregate() по фильтру
  (не цикл по отзывам в Python);
- для списка препаратов с «средней оценкой» — annotate(Avg(...)) на queryset Medication
  одним запросом (см. apps.pharmacy.selectors.medications_for_catalog), не подгружайте
  все отзывы в память.
"""
from __future__ import annotations

from decimal import Decimal

from django.db.models import Avg, Count, Q, QuerySet

from apps.reviews.models import Review, ReviewModerationStatus


def reviews_visible_for(
    *,
    user,
    medication_id: int | None = None,
) -> QuerySet[Review]:
    """
    Публично: только APPROVED.
    Автор видит свои отзывы в любом статусе; staff — все.
    """
    qs = Review.objects.select_related("user", "medication").all()
    if getattr(user, "is_staff", False):
        if medication_id is not None:
            qs = qs.filter(medication_id=medication_id)
        return qs.order_by("-created_at")
    if not getattr(user, "is_authenticated", False):
        qs = qs.filter(moderation_status=ReviewModerationStatus.APPROVED)
    else:
        qs = qs.filter(
            Q(moderation_status=ReviewModerationStatus.APPROVED) | Q(user_id=user.pk)
        )
    if medication_id is not None:
        qs = qs.filter(medication_id=medication_id)
    return qs.order_by("-created_at")


def approved_reviews_for_medication(medication_id: int, *, limit: int = 15) -> QuerySet[Review]:
    """Свежие опубликованные отзывы к карточке препарата."""
    return (
        Review.objects.filter(
            medication_id=medication_id,
            moderation_status=ReviewModerationStatus.APPROVED,
        )
        .select_related("user")
        .order_by("-created_at")[:limit]
    )


def medication_review_stats(medication_id: int) -> dict[str, Decimal | int]:
    """Один запрос: средняя оценка и число опубликованных отзывов."""
    agg = Review.objects.filter(
        medication_id=medication_id,
        moderation_status=ReviewModerationStatus.APPROVED,
    ).aggregate(avg_rating=Avg("rating"), total=Count("id"))
    avg = agg["avg_rating"]
    if avg is None:
        return {"avg_rating": Decimal("0"), "approved_count": 0}
    return {
        "avg_rating": Decimal(str(round(float(avg), 2))),
        "approved_count": int(agg["total"] or 0),
    }


def review_by_pk_for_user(*, pk: int, user) -> Review | None:
    """Детальная карточка: доступ как в reviews_visible_for."""
    return reviews_visible_for(user=user).filter(pk=pk).first()
