"""
Тонкие ModelForm для CRUD и админки.

Сложная логика (остатки, цены, интеграции) остаётся в services; формы не
дублируют queryset-фильтрацию каталога — для списка используется MedicationFilter.
"""
from __future__ import annotations

from django import forms

from apps.pharmacy.models import Category, Department, Medication


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name", "slug", "description")


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ("name", "slug", "floor", "description")


class MedicationForm(forms.ModelForm):
    class Meta:
        model = Medication
        fields = (
            "code",
            "name",
            "slug",
            "description",
            "instruction",
            "manufacturer",
            "price",
            "quantity",
            "expiration_date",
            "requires_prescription",
            "image",
            "category",
            "department",
        )
