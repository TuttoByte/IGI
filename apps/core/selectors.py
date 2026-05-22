"""Слой чтения публичного контента."""
from __future__ import annotations

from django.db.models import QuerySet

from apps.core.models import EmployeeContact, NewsArticle


def published_news() -> QuerySet[NewsArticle]:
    return NewsArticle.objects.filter(is_published=True).order_by("-published_at", "-created_at")


def news_by_slug(slug: str) -> NewsArticle | None:
    return published_news().filter(slug=slug).first()


def active_employee_contacts() -> QuerySet[EmployeeContact]:
    return EmployeeContact.objects.filter(is_active=True).order_by("sort_order", "full_name")
