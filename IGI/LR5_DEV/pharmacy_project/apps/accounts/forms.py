"""
Формы: только поля и лёгкие clean_* с вызовом валидаторов.

Сборка сущностей, роли, транзакции — в services; здесь не размещаем use-case.
"""
from __future__ import annotations

from datetime import date

from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.accounts.validators import validate_belarus_mobile_phone, validate_minimum_age_18


class StyledAuthenticationForm(AuthenticationForm):
    """Единый вид полей входа с основным шаблоном."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("autocomplete", "username" if name == "username" else "current-password")


class CustomerRegistrationForm(forms.Form):
    username = forms.CharField(label=_("Имя пользователя"), max_length=150)
    email = forms.EmailField(label=_("Email"), required=True)
    password1 = forms.CharField(label=_("Пароль"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Пароль ещё раз"), widget=forms.PasswordInput)
    birth_date = forms.DateField(
        label=_("Дата рождения"),
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    phone = forms.CharField(label=_("Телефон"), max_length=20)
    address = forms.CharField(label=_("Адрес"), widget=forms.Textarea)
    avatar = forms.ImageField(label=_("Аватар"), required=False)

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["address"].widget.attrs.setdefault("rows", 3)

    def clean_username(self) -> str:
        username = self.cleaned_data["username"]
        if get_user_model().objects.filter(username=username).exists():
            raise ValidationError(_("Пользователь с таким именем уже существует."), code="duplicate_username")
        return username

    def clean_birth_date(self) -> date:
        value: date = self.cleaned_data["birth_date"]
        validate_minimum_age_18(value)
        return value

    def clean_phone(self) -> str:
        value: str = self.cleaned_data["phone"]
        validate_belarus_mobile_phone(value)
        return value

    def clean(self) -> dict[str, object] | None:
        cleaned = super().clean()
        if cleaned is None:
            return cleaned
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            raise ValidationError(_("Пароли не совпадают."), code="password_mismatch")
        return cleaned
