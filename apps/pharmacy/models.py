"""
Доменные модели аптеки: справочники и товар (Medication).

Связи FK + PROTECT предотвращают «осиротевшие» записи при удалении справочников.
Слаг — стабильный идентификатор для URL и интеграций; денежные суммы — Decimal.
"""
from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.pharmacy.slug import SlugService


class TimeStampedModel(models.Model):
    """Единый шаблон аудита для всех сущностей домена."""

    created_at = models.DateTimeField(_("создано"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("обновлено"), auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    name = models.CharField(_("название"), max_length=255)
    slug = models.SlugField(_("слаг"), max_length=255, unique=True)
    description = models.TextField(_("описание"), blank=True)

    class Meta:
        verbose_name = _("категория")
        verbose_name_plural = _("категории")
        ordering = ("name",)
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self) -> str:
        return self.name

    def save(self, *args: object, **kwargs: object) -> None:
        SlugService.assign_if_blank(self, source_field="name")
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("pharmacy:category_detail", kwargs={"slug": self.slug})


class Department(TimeStampedModel):
    name = models.CharField(_("название"), max_length=255)
    slug = models.SlugField(_("слаг"), max_length=255, unique=True)
    floor = models.SmallIntegerField(_("этаж"))
    description = models.TextField(_("описание"), blank=True)

    class Meta:
        verbose_name = _("отдел")
        verbose_name_plural = _("отделы")
        ordering = ("floor", "name")
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["name"]),
            models.Index(fields=["floor"]),
        ]

    def __str__(self) -> str:
        return self.name

    def save(self, *args: object, **kwargs: object) -> None:
        SlugService.assign_if_blank(self, source_field="name")
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("pharmacy:department_detail", kwargs={"slug": self.slug})


class Medication(TimeStampedModel):
    code = models.CharField(_("код"), max_length=64, unique=True, db_index=True)
    name = models.CharField(_("название"), max_length=255)
    slug = models.SlugField(_("слаг"), max_length=255, unique=True)
    description = models.TextField(_("описание"), blank=True)
    instruction = models.TextField(_("инструкция"), blank=True)
    manufacturer = models.CharField(_("производитель"), max_length=255)
    price = models.DecimalField(
        _("цена"),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    quantity = models.PositiveIntegerField(_("остаток"), default=0)
    expiration_date = models.DateField(_("срок годности"))
    requires_prescription = models.BooleanField(_("рецепт обязателен"), default=False)
    image = models.ImageField(
        _("изображение"),
        upload_to="medications/%Y/%m/",
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        Category,
        verbose_name=_("категория"),
        on_delete=models.PROTECT,
        related_name="medications",
    )
    department = models.ForeignKey(
        Department,
        verbose_name=_("отдел"),
        on_delete=models.PROTECT,
        related_name="medications",
    )

    class Meta:
        verbose_name = _("препарат")
        verbose_name_plural = _("препараты")
        ordering = ("name",)
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["name"]),
            models.Index(fields=["code"]),
            models.Index(fields=["expiration_date"]),
            models.Index(fields=["requires_prescription"]),
            models.Index(fields=["category", "department"]),
            models.Index(fields=["price"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"

    def save(self, *args: object, **kwargs: object) -> None:
        SlugService.assign_if_blank(self, source_field="name")
        super().save(*args, **kwargs)

    def is_expired(self) -> bool:
        """Срок годности истёк относительно текущей даты в текущей таймзоне проекта."""
        return self.expiration_date < timezone.now().date()

    def is_low_stock(self) -> bool:
        """Порог остатка задаётся настройкой — единая политика для UI и отчётов."""
        threshold: int = int(getattr(settings, "PHARMACY_LOW_STOCK_THRESHOLD", 10))
        return int(self.quantity) <= threshold

    def get_absolute_url(self) -> str:
        return reverse("pharmacy:medication_detail", kwargs={"slug": self.slug})
