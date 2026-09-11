"""Счётчик корзины в шапке сайта — доступен во всех шаблонах."""
from __future__ import annotations

from apps.cart.cart import Cart


def cart_summary(request) -> dict[str, int]:
    cart = Cart(request)
    return {"cart_total_quantity": cart.total_quantity}
