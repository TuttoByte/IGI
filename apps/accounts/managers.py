"""Менеджер пользователя: инкапсулирует создание записей с инвариантами."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any

from django.contrib.auth.models import AbstractUser, BaseUserManager

if TYPE_CHECKING:
    from apps.accounts.models import CustomUser


class CustomUserManager(BaseUserManager["CustomUser"]):
    """
    Централизованное создание пользователей.

    Суперпользователь всегда получает связанный Profile, чтобы не нарушать
    OneToOne и будущие предположения кода (селекторы, сериализаторы).
    """

    use_in_migrations = True

    def create_user(
        self,
        username: str,
        email: str | None = None,
        password: str | None = None,
        **extra_fields: Any,
    ) -> CustomUser:
        if not username:
            raise ValueError("username is required")
        user = self.model(username=username, email=email or "", **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        username: str,
        email: str | None = None,
        password: str | None = None,
        **extra_fields: Any,
    ) -> CustomUser:
        from apps.accounts.models import Profile, UserRole

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", UserRole.ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        user = self.create_user(username, email, password, **extra_fields)
        # Минимально валидные данные для инвариантов Profile (dev/CLI).
        Profile.objects.create(
            user=user,
            birth_date=date(1970, 1, 1),
            phone="+375 (29) 000-00-00",
            address="—",
        )
        return user
