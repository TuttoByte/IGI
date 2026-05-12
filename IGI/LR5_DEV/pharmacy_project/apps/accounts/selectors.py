"""
Слой чтения (selectors): только запросы и сборка DTO/моделей без побочных эффектов.

Такой слой упрощает кэширование, пагинацию и смену ORM в будущем — views и
сервисы не строят «сырые» QuerySet-цепочки по всему проекту.
"""
from __future__ import annotations

from django.db.models import QuerySet

from apps.accounts.models import CustomUser, Profile, UserRole


def user_with_profile_by_id(user_id: int) -> CustomUser | None:
    """Один пользователь с профилем (select_related) — типичный hot-path."""
    return (
        CustomUser.objects.select_related("profile")
        .filter(pk=user_id)
        .first()
    )


def user_with_profile_by_username(username: str) -> CustomUser | None:
    return (
        CustomUser.objects.select_related("profile")
        .filter(username=username)
        .first()
    )


def active_users_by_role(role: UserRole | str) -> QuerySet[CustomUser]:
    """Фильтр по роли + активность — индексируемое поле role используется в Meta."""
    value = role.value if isinstance(role, UserRole) else role
    return CustomUser.objects.filter(role=value, is_active=True).order_by("id")


def profiles_created_since(limit: int = 100) -> QuerySet[Profile]:
    """Пример списка для админ-дашбордов / отчётов (срез для масштабирования)."""
    return Profile.objects.select_related("user").order_by("-created_at")[:limit]
