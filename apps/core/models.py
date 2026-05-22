"""Публичный контент сайта: новости и контакты сотрудников."""
from __future__ import annotations

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.pharmacy.slug import SlugService


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(_("создано"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("обновлено"), auto_now=True)

    class Meta:
        abstract = True


class NewsArticle(TimeStampedModel):
    """Новость аптеки: публикация всегда с изображением."""

    title = models.CharField(_("заголовок"), max_length=255)
    slug = models.SlugField(_("слаг"), max_length=255, unique=True)
    image = models.ImageField(_("изображение"), upload_to="news/%Y/%m/")
    lead = models.TextField(_("анонс"))
    content = models.TextField(_("текст новости"))
    published_at = models.DateTimeField(_("дата публикации"), default=timezone.now, db_index=True)
    is_published = models.BooleanField(_("опубликовано"), default=True, db_index=True)

    class Meta:
        verbose_name = _("новость")
        verbose_name_plural = _("новости")
        ordering = ("-published_at", "-created_at")
        indexes = [
            models.Index(fields=["is_published", "-published_at"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["title"]),
        ]

    def __str__(self) -> str:
        return self.title

    def save(self, *args: object, **kwargs: object) -> None:
        SlugService.assign_if_blank(self, source_field="title", max_length=80)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("core:news_detail", kwargs={"slug": self.slug})


class EmployeeContact(TimeStampedModel):
    """Карточка сотрудника для страницы контактов."""

    full_name = models.CharField(_("ФИО"), max_length=255)
    slug = models.SlugField(_("слаг"), max_length=255, unique=True)
    position = models.CharField(_("должность"), max_length=255)
    photo = models.ImageField(_("фотография"), upload_to="employees/%Y/%m/")
    phone = models.CharField(_("телефон"), max_length=40, blank=True)
    email = models.EmailField(_("email"), blank=True)
    work_calendar = models.TextField(_("текстовый календарь"))
    note = models.TextField(_("информация"), blank=True)
    sort_order = models.PositiveSmallIntegerField(_("порядок"), default=100, db_index=True)
    is_active = models.BooleanField(_("показывать на сайте"), default=True, db_index=True)

    class Meta:
        verbose_name = _("контакт сотрудника")
        verbose_name_plural = _("контакты сотрудников")
        ordering = ("sort_order", "full_name")
        indexes = [
            models.Index(fields=["is_active", "sort_order", "full_name"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self) -> str:
        return self.full_name

    def save(self, *args: object, **kwargs: object) -> None:
        SlugService.assign_if_blank(self, source_field="full_name", max_length=80)
        super().save(*args, **kwargs)
