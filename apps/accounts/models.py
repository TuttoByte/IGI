"""Модели домена учётных записей."""
from __future__ import annotations

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.managers import CustomUserManager
from apps.accounts.validators import validate_belarus_mobile_phone, validate_minimum_age_18


class UserRole(models.TextChoices):
    """Роли на уровне предметной области (расширяемы без смены схемы auth.Group)."""

    ADMIN = "ADMIN", _("Администратор")
    EMPLOYEE = "EMPLOYEE", _("Сотрудник")
    CUSTOMER = "CUSTOMER", _("Клиент")


class CustomUser(AbstractUser):
    """
    Кастомный пользователь на базе AbstractUser.

    Поле role — явная бизнес-роль; is_staff/is_superuser остаются для
    совместимости с Django Admin и внутренними проверками фреймворка.
    """

    role = models.CharField(
        _("роль"),
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CUSTOMER,
        db_index=True,
    )

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("пользователь")
        verbose_name_plural = _("пользователи")
        indexes = [
            models.Index(fields=["role", "is_active"]),
        ]

    def __str__(self) -> str:
        return self.username


class Profile(models.Model):
    """
    Расширяющий профиль 1:1.

    Вынесен отдельно от CustomUser, чтобы масштабировать домен (адреса,
    документы, согласия) без раздувания таблицы auth-полей.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("пользователь"),
    )
    avatar = models.ImageField(
        _("аватар"),
        upload_to="avatars/%Y/%m/",
        blank=True,
        null=True,
    )
    birth_date = models.DateField(_("дата рождения"), validators=[validate_minimum_age_18])
    phone = models.CharField(
        _("телефон"),
        max_length=20,
        validators=[validate_belarus_mobile_phone],
    )
    timezone = models.CharField(_("часовой пояс"), max_length=64, default=settings.TIME_ZONE)
    address = models.TextField(_("адрес"))
    created_at = models.DateTimeField(_("создан"), auto_now_add=True)
    updated_at = models.DateTimeField(_("обновлён"), auto_now=True)

    class Meta:
        verbose_name = _("профиль")
        verbose_name_plural = _("профили")
        indexes = [
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self) -> str:
        return f"Profile({self.user_id})"
