"""Генерация уникальных slug без зависимости от models (избегаем циклических импортов)."""
from __future__ import annotations

from typing import Any

from django.db import models
from django.utils.text import slugify


class SlugService:
    """
    Единая точка для человекочитаемых URL.
    """

    @staticmethod
    def assign_if_blank(
        instance: models.Model,
        *,
        source_field: str = "name",
        slug_field: str = "slug",
        max_length: int = 50,
    ) -> None:
        current = getattr(instance, slug_field, None)
        if current:
            return
        raw = getattr(instance, source_field, "") or "item"
        base = slugify(str(raw))[:max_length] or "item"
        Model = instance.__class__
        slug = base
        suffix = 2
        qs: models.QuerySet[Any] = Model.objects.all()
        if instance.pk:
            qs = qs.exclude(pk=instance.pk)
        while qs.filter(**{slug_field: slug}).exists():
            extra = f"-{suffix}"
            slug = f"{base[: max_length - len(extra)]}{extra}"
            suffix += 1
        setattr(instance, slug_field, slug)
