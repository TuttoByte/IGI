"""
Корзина заказа поверх сессии.

Почему сессия, а не таблица: корзина живёт до оплаты, принадлежит браузеру и
не требует авторизации — заказ фиксируется уже на странице оплаты. Хранится
компактно: {"<medication_id>": количество}. Цена и остаток всегда читаются из
БД в момент отображения, поэтому «замороженных» цен в сессии не возникает.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from django.conf import settings

from apps.pharmacy.models import Medication

CART_SESSION_KEY = "cart"
MAX_ITEM_QUANTITY = 99
DELIVERY_PRICE = Decimal(str(getattr(settings, "PHARMACY_DELIVERY_PRICE", "4.90")))
FREE_DELIVERY_FROM = Decimal(str(getattr(settings, "PHARMACY_FREE_DELIVERY_FROM", "60.00")))


@dataclass(frozen=True)
class CartLine:
    """Строка корзины: препарат, количество и стоимость позиции."""

    medication: Medication
    quantity: int

    @property
    def total_price(self) -> Decimal:
        return self.medication.price * self.quantity

    @property
    def exceeds_stock(self) -> bool:
        return self.quantity > self.medication.quantity


class Cart:
    """Операции над корзиной: добавление, изменение количества, удаление, итоги."""

    def __init__(self, request) -> None:
        self.session = request.session
        raw = self.session.get(CART_SESSION_KEY)
        self._items: dict[str, int] = dict(raw) if isinstance(raw, dict) else {}

    # --- запись -----------------------------------------------------------
    def add(self, medication_id: int, quantity: int = 1) -> int:
        """Добавляет количество к позиции и возвращает новое значение."""
        key = str(int(medication_id))
        current = self._items.get(key, 0)
        return self.set_quantity(medication_id, current + max(1, int(quantity)))

    def set_quantity(self, medication_id: int, quantity: int) -> int:
        """Жёстко задаёт количество; 0 и меньше удаляет позицию."""
        key = str(int(medication_id))
        quantity = min(int(quantity), MAX_ITEM_QUANTITY)
        if quantity <= 0:
            self._items.pop(key, None)
            self._save()
            return 0
        self._items[key] = quantity
        self._save()
        return quantity

    def change_quantity(self, medication_id: int, delta: int) -> int:
        """«Увеличить/уменьшить количество товаров» на странице корзины."""
        key = str(int(medication_id))
        return self.set_quantity(medication_id, self._items.get(key, 0) + int(delta))

    def remove(self, medication_id: int) -> None:
        self._items.pop(str(int(medication_id)), None)
        self._save()

    def clear(self) -> None:
        self._items = {}
        self.session.pop(CART_SESSION_KEY, None)
        self.session.modified = True

    def _save(self) -> None:
        self.session[CART_SESSION_KEY] = self._items
        self.session.modified = True

    # --- чтение -----------------------------------------------------------
    def lines(self) -> list[CartLine]:
        """Позиции корзины одним запросом к БД; исчезнувшие товары отсеиваются."""
        if not self._items:
            return []
        ids = [int(key) for key in self._items]
        found = Medication.objects.select_related("category", "department").filter(pk__in=ids)
        by_id = {med.pk: med for med in found}
        return [
            CartLine(medication=by_id[int(key)], quantity=qty)
            for key, qty in self._items.items()
            if int(key) in by_id
        ]

    def __len__(self) -> int:
        return sum(self._items.values())

    def __bool__(self) -> bool:
        return bool(self._items)

    @property
    def total_quantity(self) -> int:
        return len(self)

    def totals(self) -> dict[str, Decimal | int]:
        """Итоги заказа: сумма позиций, доставка и общая сумма к оплате."""
        lines = self.lines()
        subtotal = sum((line.total_price for line in lines), Decimal("0"))
        delivery = Decimal("0") if not lines or subtotal >= FREE_DELIVERY_FROM else DELIVERY_PRICE
        return {
            "positions": len(lines),
            "quantity": sum(line.quantity for line in lines),
            "subtotal": subtotal,
            "delivery": delivery,
            "total": subtotal + delivery,
        }
