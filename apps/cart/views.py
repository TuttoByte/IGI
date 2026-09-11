"""
Корзина и оплата.

Изменяющие операции — только POST с CSRF-токеном: GET-ссылка «удалить» ломается
о префетч браузера и не должна менять состояние.
"""
from __future__ import annotations

from decimal import Decimal

from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import FormView, TemplateView

from apps.cart.cart import FREE_DELIVERY_FROM, Cart
from apps.cart.forms import PaymentForm
from apps.core import selectors as core_selectors
from apps.pharmacy.models import Medication

LAST_ORDER_SESSION_KEY = "last_order"


def _back_to_cart(request) -> HttpResponseRedirect:
    return redirect(request.POST.get("next") or reverse("cart:detail"))


class CartDetailView(TemplateView):
    """Страница корзины: позиции, количество, итоги и переход к оплате."""

    template_name = "frontend/cart/cart_detail.html"

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        ctx = super().get_context_data(**kwargs)
        cart = Cart(self.request)
        ctx["lines"] = cart.lines()
        ctx["totals"] = cart.totals()
        ctx["free_delivery_from"] = FREE_DELIVERY_FROM
        ctx["promos"] = core_selectors.current_promo_codes()[:3]
        return ctx


@require_POST
def cart_add(request, medication_id: int) -> HttpResponse:
    """«Добавить в корзину» с карточки товара или из каталога."""
    medication = get_object_or_404(Medication, pk=medication_id)
    try:
        quantity = int(request.POST.get("quantity", "1"))
    except (TypeError, ValueError):
        quantity = 1
    Cart(request).add(medication.pk, quantity)
    messages.success(request, f"«{medication.name}» — в корзине.")
    return redirect(request.POST.get("next") or reverse("cart:detail"))


@require_POST
def cart_change(request, medication_id: int) -> HttpResponse:
    """«Увеличить/уменьшить количество товаров» на странице корзины."""
    delta = 1 if request.POST.get("action") == "increase" else -1
    cart = Cart(request)
    if cart.change_quantity(medication_id, delta) == 0:
        messages.info(request, "Позиция удалена из корзины.")
    return _back_to_cart(request)


@require_POST
def cart_set_quantity(request, medication_id: int) -> HttpResponse:
    """Ручной ввод количества полем <input type=number>."""
    try:
        quantity = int(request.POST.get("quantity", "1"))
    except (TypeError, ValueError):
        messages.error(request, "Количество должно быть целым числом.")
        return _back_to_cart(request)
    Cart(request).set_quantity(medication_id, quantity)
    return _back_to_cart(request)


@require_POST
def cart_remove(request, medication_id: int) -> HttpResponse:
    """«Удалить из корзины»."""
    Cart(request).remove(medication_id)
    messages.info(request, "Позиция удалена из корзины.")
    return _back_to_cart(request)


@require_POST
def cart_clear(request) -> HttpResponse:
    Cart(request).clear()
    messages.info(request, "Корзина очищена.")
    return redirect("cart:detail")


class CheckoutView(FormView):
    """Страница оплаты товаров: форма с валидацией и расчётом итогов."""

    template_name = "frontend/cart/checkout.html"
    form_class = PaymentForm

    def dispatch(self, request, *args: object, **kwargs: object):
        self.cart = Cart(request)
        if not self.cart and request.method == "GET":
            messages.info(request, "Корзина пуста — добавьте товары перед оплатой.")
            return redirect("cart:detail")
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self) -> dict[str, object]:
        initial = super().get_initial()
        user = self.request.user
        if user.is_authenticated:
            full_name = f"{user.last_name} {user.first_name}".strip()
            initial["full_name"] = full_name or user.username
            initial["email"] = user.email
            profile = getattr(user, "profile", None)
            if profile is not None:
                initial["phone"] = profile.phone
                initial["address"] = profile.address
        return initial

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        ctx = super().get_context_data(**kwargs)
        ctx["lines"] = self.cart.lines()
        ctx["totals"] = self.cart.totals()
        ctx["promos"] = core_selectors.current_promo_codes()
        return ctx

    def form_valid(self, form: PaymentForm) -> HttpResponse:
        totals = self.cart.totals()
        promo = form.promo
        discount = Decimal("0")
        if promo is not None:
            discount = (Decimal(totals["subtotal"]) * promo.discount_percent / 100).quantize(
                Decimal("0.01")
            )
        payable = Decimal(totals["total"]) - discount
        self.request.session[LAST_ORDER_SESSION_KEY] = {
            "full_name": form.cleaned_data["full_name"],
            "email": form.cleaned_data["email"],
            "phone": form.cleaned_data["phone"],
            "delivery_method": form.cleaned_data["delivery_method"],
            "delivery_date": form.cleaned_data["delivery_date"].isoformat(),
            "payment_method": form.cleaned_data["payment_method"],
            "promo_code": form.cleaned_data.get("promo_code", ""),
            "positions": totals["positions"],
            "quantity": totals["quantity"],
            "subtotal": str(totals["subtotal"]),
            "delivery": str(totals["delivery"]),
            "discount": str(discount),
            "total": str(max(payable, Decimal("0"))),
            "items": [
                {"name": line.medication.name, "quantity": line.quantity, "sum": str(line.total_price)}
                for line in self.cart.lines()
            ],
        }
        self.cart.clear()
        messages.success(self.request, "Оплата прошла успешно. Заказ передан в аптеку.")
        return redirect("cart:success")


class PaymentSuccessView(TemplateView):
    """Чек об оплате: читает итог заказа из сессии."""

    template_name = "frontend/cart/success.html"

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        ctx = super().get_context_data(**kwargs)
        ctx["order"] = self.request.session.get(LAST_ORDER_SESSION_KEY)
        return ctx
