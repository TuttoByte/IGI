"""
Создание продажи: единая транзакция, проверка остатков, строки, списание склада.

Списание остатка делегируется MedicationInventoryService — одна реализация,
без дублирования F()-обновлений в двух приложениях.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from apps.pharmacy.models import Medication
from apps.pharmacy.services import MedicationInventoryService
from apps.sales.models import Sale, SaleItem, SaleStatus


@dataclass(frozen=True, slots=True)
class SaleLineInput:
    medication_id: int
    quantity: int


class SaleService:
    """Оформление продажи: строки, суммы, списание остатков."""

    @staticmethod
    def _merge_quantities(lines: Sequence[SaleLineInput]) -> dict[int, int]:
        merged: dict[int, int] = defaultdict(int)
        for line in lines:
            if line.quantity <= 0:
                raise ValidationError(_("Количество должно быть положительным."), code="invalid_qty")
            merged[line.medication_id] += line.quantity
        return dict(merged)

    @staticmethod
    @transaction.atomic
    def create_completed_sale(
        *,
        customer_id: int,
        employee_id: int,
        lines: Sequence[SaleLineInput],
    ) -> Sale:
        if not lines:
            raise ValidationError(_("Добавьте хотя бы одну позицию."), code="empty_sale")

        merged = SaleService._merge_quantities(lines)

        priced: dict[int, tuple[Medication, int, Decimal, Decimal]] = {}
        total = Decimal("0.00")

        for mid in sorted(merged.keys()):
            med = Medication.objects.select_for_update().get(pk=mid)
            qty = merged[mid]
            if med.quantity < qty:
                raise ValidationError(
                    _("Недостаточно «%(name)s» на складе (нужно %(need)s, есть %(have)s).")
                    % {"name": med.name, "need": qty, "have": med.quantity},
                    code="insufficient_stock",
                )
            unit = med.price
            subtotal = (unit * qty).quantize(Decimal("0.01"))
            total += subtotal
            priced[mid] = (med, qty, unit, subtotal)

        sale = Sale.objects.create(
            customer_id=customer_id,
            employee_id=employee_id,
            status=SaleStatus.COMPLETED,
            total_price=total,
        )

        for _mid, (med, qty, unit, subtotal) in priced.items():
            SaleItem.objects.create(
                sale=sale,
                medication=med,
                quantity=qty,
                price=unit,
                subtotal=subtotal,
            )

        for _mid, (med, qty, _unit, _subtotal) in priced.items():
            MedicationInventoryService.apply_stock_delta(med.pk, -qty)

        return sale
