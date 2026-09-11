"""Слой чтения публичного контента."""
from __future__ import annotations

from django.db.models import QuerySet
from django.utils import timezone

from apps.core.models import (
    Banner,
    CompanyInfo,
    EmployeeContact,
    GlossaryTerm,
    NewsArticle,
    Partner,
    PromoCode,
    Vacancy,
)


def published_news() -> QuerySet[NewsArticle]:
    return NewsArticle.objects.filter(is_published=True).order_by("-published_at", "-created_at")


def news_by_slug(slug: str) -> NewsArticle | None:
    return published_news().filter(slug=slug).first()


def active_employee_contacts() -> QuerySet[EmployeeContact]:
    return EmployeeContact.objects.filter(is_active=True).order_by("sort_order", "full_name")


def latest_published_article() -> NewsArticle | None:
    """Последняя опубликованная статья для анонса на главной."""
    return published_news().first()


def active_banners() -> QuerySet[Banner]:
    return Banner.objects.filter(is_active=True).order_by("sort_order", "-created_at")


def active_partners() -> QuerySet[Partner]:
    return Partner.objects.filter(is_active=True).order_by("sort_order", "name")


def company_info() -> CompanyInfo | None:
    """Синглтон «О компании» вместе с историей по годам — один запрос + prefetch."""
    return (
        CompanyInfo.objects.filter(is_active=True)
        .prefetch_related("milestones")
        .order_by("-updated_at")
        .first()
    )


def published_glossary_terms() -> QuerySet[GlossaryTerm]:
    return GlossaryTerm.objects.filter(is_published=True).order_by("sort_order", "term")


def open_vacancies() -> QuerySet[Vacancy]:
    return (
        Vacancy.objects.filter(is_open=True)
        .select_related("department")
        .order_by("-published_at", "title")
    )


def current_promo_codes() -> QuerySet[PromoCode]:
    """Действующие промокоды: включены и сегодняшняя дата внутри окна."""
    today = timezone.localdate()
    return PromoCode.objects.filter(
        is_active=True,
        valid_from__lte=today,
        valid_to__gte=today,
    ).order_by("valid_to", "code")


def archived_promo_codes() -> QuerySet[PromoCode]:
    """Архив: срок истёк, ещё не начался или промокод выключен."""
    today = timezone.localdate()
    return PromoCode.objects.exclude(
        is_active=True,
        valid_from__lte=today,
        valid_to__gte=today,
    ).order_by("-valid_to", "code")
