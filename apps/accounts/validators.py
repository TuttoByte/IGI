"""
Переиспользуемые валидаторы полей (модели, формы, сервисы).

Дублирование вызовов из форм и сервисов намеренное: формы дают быстрый UX,
сервисы — защитную проверку при масштабировании (API, команды, очереди).
"""
from __future__ import annotations

import re
from datetime import date

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# Код оператора 29 (МТС) в формате, заданном в ТЗ.
PHONE_PATTERN = re.compile(r"^\+375 \(29\) \d{3}-\d{2}-\d{2}$")


def validate_belarus_mobile_phone(value: str) -> None:
    if not PHONE_PATTERN.fullmatch(value):
        raise ValidationError(
            _("Телефон должен быть в формате: +375 (29) XXX-XX-XX."),
            code="invalid_phone_format",
        )


def validate_minimum_age_18(birth_date: date) -> None:
    """Пользователь должен быть не моложе 18 лет на текущую дату."""
    today = date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    if age < 18:
        raise ValidationError(
            _("Регистрация доступна только с 18 лет."),
            code="underage",
        )
