"""
Слой команд / политик домена (остатки, переносы и т.д.).

Изменение количества и инварианты склада — не в views и не в ModelForm.save().
"""
from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.pharmacy.models import Medication


class MedicationInventoryService:
    """Операции со складскими остатками в одной транзакции."""

    @staticmethod
    def apply_stock_delta(medication_id: int, delta: int) -> Medication:
        qs = Medication.objects.select_for_update().select_related("category", "department")
        medication = qs.get(pk=medication_id)
        new_qty = int(medication.quantity) + int(delta)
        if new_qty < 0:
            raise ValidationError(_("Недостаточно товара на складе."), code="insufficient_stock")
        Medication.objects.filter(pk=medication_id).update(
            quantity=new_qty,
            updated_at=timezone.now(),
        )
        medication.refresh_from_db(fields=["quantity", "updated_at"])
        return medication


class MedicationPricingService:
    """Пример отдельного сервиса под ценообразование (масштабирование по домену)."""

    @staticmethod
    def set_price(medication_id: int, *, new_price: Decimal) -> Medication:
        if new_price < 0:
            raise ValidationError(_("Цена не может быть отрицательной."), code="invalid_price")
        Medication.objects.filter(pk=medication_id).update(
            price=new_price,
            updated_at=timezone.now(),
        )
        return Medication.objects.get(pk=medication_id)
