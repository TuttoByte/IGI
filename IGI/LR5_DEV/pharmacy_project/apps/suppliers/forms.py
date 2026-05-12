"""ModelForm для CRUD поставщика (включая M2M препараты)."""
from __future__ import annotations

from django import forms

from apps.suppliers.models import Supplier


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = (
            "name",
            "slug",
            "email",
            "phone",
            "address",
            "contract_number",
            "medications",
        )
        widgets = {
            "slug": forms.TextInput(attrs={"placeholder": "Оставьте пустым — сгенерируется из названия"}),
            "address": forms.Textarea(attrs={"rows": 3}),
        }
