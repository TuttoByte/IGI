"""
Отзывы на препараты с модерацией.

Один пользователь — один отзыв на медикамент: UniqueConstraint (user, medication).
Публично показываются только записи со статусом APPROVED (см. selectors).
"""
from __future__ import annotations

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class ReviewModerationStatus(models.TextChoices):
    PENDING = "PENDING", _("На модерации")
    APPROVED = "APPROVED", _("Опубликован")
    REJECTED = "REJECTED", _("Отклонён")


class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("автор"),
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    medication = models.ForeignKey(
        "pharmacy.Medication",
        verbose_name=_("препарат"),
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField(
        _("оценка"),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    text = models.TextField(_("текст"), blank=True)
    moderation_status = models.CharField(
        _("модерация"),
        max_length=20,
        choices=ReviewModerationStatus.choices,
        default=ReviewModerationStatus.PENDING,
        db_index=True,
    )
    created_at = models.DateTimeField(_("создано"), auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _("отзыв")
        verbose_name_plural = _("отзывы")
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(fields=("user", "medication"), name="reviews_unique_user_medication"),
        ]
        indexes = [
            models.Index(fields=["medication", "moderation_status", "-created_at"], name="reviews_rev_med_md_crd_idx"),
            models.Index(fields=["medication", "moderation_status", "-rating"], name="reviews_rev_med_md_rt_idx"),
            models.Index(fields=["user", "-created_at"], name="reviews_rev_usr_crd_idx"),
        ]

    def __str__(self) -> str:
        return f"Review({self.medication_id}) {self.rating}★"

    def get_absolute_url(self) -> str:
        return reverse("reviews:review_detail", kwargs={"pk": self.pk})
