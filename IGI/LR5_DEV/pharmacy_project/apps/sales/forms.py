"""Формы оформления продажи: шапка чека + formset строк (без ORM-логики)."""
from __future__ import annotations

from django import forms
from django.contrib.auth import get_user_model
from django.forms import formset_factory

from apps.accounts.models import UserRole
from apps.pharmacy.models import Medication

User = get_user_model()


class SaleHeaderForm(forms.Form):
    customer = forms.ModelChoiceField(
        label="Покупатель",
        queryset=User.objects.filter(role=UserRole.CUSTOMER, is_active=True).order_by("username"),
    )
    employee = forms.ModelChoiceField(
        label="Сотрудник",
        queryset=User.objects.filter(
            role__in=(UserRole.ADMIN, UserRole.EMPLOYEE),
            is_active=True,
        ).order_by("username"),
    )


class SaleLineForm(forms.Form):
    medication = forms.ModelChoiceField(
        label="Препарат",
        queryset=Medication.objects.select_related("category", "department").order_by("name"),
    )
    quantity = forms.IntegerField(label="Кол-во", min_value=1)


SaleLineFormSet = formset_factory(
    SaleLineForm,
    extra=2,
    min_num=1,
    validate_min=True,
    can_delete=True,
)
