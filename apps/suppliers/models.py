"""
Модель поставщика и связь с препаратами.

Почему ManyToMany (а не ForeignKey «один поставщик на препарат»):
- один и тот же препарат могут поставлять разные юрлица (параллельный импорт,
  региональные дистрибьюторы, смена контракта во времени без дублирования карточки товара);
- один поставщик везёт множество SKU — классическая M2M.

Поле M2M объявлено на стороне Supplier (`medications`), чтобы в Django Admin
удобно использовать filter_horizontal и не дублировать связь вторым полем
на Medication (обратная сторона — `Medication.suppliers` через related_name).
"""
from __future__ import annotations

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.accounts.validators import validate_belarus_mobile_phone
from apps.pharmacy.slug import SlugService


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(_("создано"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("обновлено"), auto_now=True)

    class Meta:
        abstract = True


class Supplier(TimeStampedModel):
    name = models.CharField(_("название"), max_length=255)
    slug = models.SlugField(_("слаг"), max_length=255, unique=True)
    email = models.EmailField(_("email"))
    phone = models.CharField(_("телефон"), max_length=20, validators=[validate_belarus_mobile_phone])
    address = models.TextField(_("адрес"))
    contract_number = models.CharField(_("номер договора"), max_length=128, unique=True, db_index=True)

    medications = models.ManyToManyField(
        "pharmacy.Medication",
        verbose_name=_("препараты"),
        related_name="suppliers",
        blank=True,
    )

    class Meta:
        verbose_name = _("поставщик")
        verbose_name_plural = _("поставщики")
        ordering = ("name",)
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["name"]),
            models.Index(fields=["email"]),
            models.Index(fields=["contract_number"]),
        ]

    def __str__(self) -> str:
        return self.name

    def save(self, *args: object, **kwargs: object) -> None:
        SlugService.assign_if_blank(self, source_field="name")
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("suppliers:supplier_detail", kwargs={"slug": self.slug})
