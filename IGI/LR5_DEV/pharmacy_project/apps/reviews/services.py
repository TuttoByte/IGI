"""
Создание / изменение / удаление отзывов (инварианты, без «толстых» моделей).
"""
from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils.translation import gettext_lazy as _

from apps.reviews.models import Review, ReviewModerationStatus


class ReviewService:
    @staticmethod
    @transaction.atomic
    def create_review(
        *,
        user,
        medication_id: int,
        rating: int,
        text: str,
    ) -> Review:
        if not getattr(user, "is_authenticated", False):
            raise ValidationError(_("Только для авторизованных пользователей."))
        try:
            return Review.objects.create(
                user=user,
                medication_id=medication_id,
                rating=rating,
                text=text,
                moderation_status=ReviewModerationStatus.PENDING,
            )
        except IntegrityError as exc:
            raise ValidationError(
                _("Вы уже оставляли отзыв на этот препарат."),
                code="duplicate_review",
            ) from exc

    @staticmethod
    @transaction.atomic
    def update_review(*, review: Review, user, rating: int, text: str) -> Review:
        if not (user.is_staff or review.user_id == user.pk):
            raise ValidationError(_("Нельзя редактировать чужой отзыв."), code="forbidden")
        review.rating = rating
        review.text = text
        if not user.is_staff:
            review.moderation_status = ReviewModerationStatus.PENDING
        review.save(update_fields=["rating", "text", "moderation_status"])
        return review

    @staticmethod
    @transaction.atomic
    def delete_review(*, review: Review, user) -> None:
        if not (user.is_staff or review.user_id == user.pk):
            raise ValidationError(_("Нельзя удалить чужой отзыв."), code="forbidden")
        review.delete()
