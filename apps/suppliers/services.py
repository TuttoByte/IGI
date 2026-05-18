"""
Команды домена: атомарное сохранение поставщика и связей M2M.

ModelForm уже валидирует поля; сервис фиксирует транзакционную границу и место
для будущих побочных эффектов (аудит, интеграция с 1С, уведомления).
"""
from __future__ import annotations

from django.db import transaction

from apps.suppliers.forms import SupplierForm
from apps.suppliers.models import Supplier


class SupplierService:
    @staticmethod
    @transaction.atomic
    def save_from_form(form: SupplierForm) -> Supplier:
        supplier = form.save(commit=False)
        supplier.save()
        form.save_m2m()
        return supplier

    @staticmethod
    @transaction.atomic
    def delete(supplier: Supplier) -> None:
        supplier.delete()
