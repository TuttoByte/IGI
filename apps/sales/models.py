"""
Модели продаж: заголовок чека (Sale) и строки (SaleItem).

Итоги total_price / subtotal не считаются в save() моделей (без «толстых» моделей) —
агрегаты выставляет слой services при создании проводки.
"""
from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class SaleStatus(models.TextChoices):
    DRAFT = "DRAFT", _("Черновик")
    COMPLETED = "COMPLETED", _("Проведена")
    CANCELLED = "CANCELLED", _("Отменена")


class Sale(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("покупатель"),
        on_delete=models.PROTECT,
        related_name="sales_as_customer",
    )
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("сотрудник"),
        on_delete=models.PROTECT,
        related_name="sales_as_employee",
    )
    created_at = models.DateTimeField(_("создано"), auto_now_add=True, db_index=True)
    status = models.CharField(
        _("статус"),
        max_length=20,
        choices=SaleStatus.choices,
        default=SaleStatus.COMPLETED,
        db_index=True,
    )
    total_price = models.DecimalField(
        _("сумма"),
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0"))],
    )

    class Meta:
        verbose_name = _("продажа")
        verbose_name_plural = _("продажи")
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["-created_at", "status"]),
            models.Index(fields=["customer", "-created_at"]),
            models.Index(fields=["employee", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"Sale #{self.pk} {self.total_price}"

    def get_absolute_url(self) -> str:
        return reverse("sales:sale_detail", kwargs={"pk": self.pk})


class SaleItem(models.Model):
    sale = models.ForeignKey(
        Sale,
        verbose_name=_("продажа"),
        on_delete=models.CASCADE,
        related_name="items",
    )
    medication = models.ForeignKey(
        "pharmacy.Medication",
        verbose_name=_("препарат"),
        on_delete=models.PROTECT,
        related_name="sale_items",
    )
    quantity = models.PositiveIntegerField(_("количество"))
    price = models.DecimalField(
        _("цена за единицу"),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    subtotal = models.DecimalField(
        _("сумма строки"),
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )

    class Meta:
        verbose_name = _("строка продажи")
        verbose_name_plural = _("строки продаж")
        ordering = ("pk",)
        indexes = [
            models.Index(fields=["sale", "medication"]),
        ]

    def __str__(self) -> str:
        return f"{self.medication_id}×{self.quantity}"
