"""
Слой use-case / команд (services): транзакции, инварианты, вызовы внешних систем.

Views остаются тонкими: валидируют форму и делегируют сюда. При появлении REST
или Celery-задач те же функции/классы переиспользуются без копирования логики.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from apps.accounts.models import CustomUser, Profile, UserRole
from apps.accounts.validators import validate_belarus_mobile_phone, validate_minimum_age_18

User = get_user_model()


@dataclass(frozen=True, slots=True)
class CustomerRegistrationDTO:
    """Явный контракт входных данных — проще типизировать и версионировать API."""

    username: str
    email: str
    password: str
    birth_date: date
    phone: str
    timezone: str
    address: str
    avatar: UploadedFile | None = None


class RegistrationService:
    """Регистрация клиента: создание пользователя и связанного профиля."""

    @staticmethod
    @transaction.atomic
    def register_customer(dto: CustomerRegistrationDTO) -> CustomUser:
        # Защитная валидация помимо формы (не доверяем только HTTP-слою).
        validate_minimum_age_18(dto.birth_date)
        validate_belarus_mobile_phone(dto.phone)

        user = User.objects.create_user(
            username=dto.username,
            email=dto.email,
            password=dto.password,
            role=UserRole.CUSTOMER,
        )
        Profile.objects.create(
            user=user,
            birth_date=dto.birth_date,
            phone=dto.phone,
            timezone=dto.timezone,
            address=dto.address,
            avatar=dto.avatar,
        )
        return user
