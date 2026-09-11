"""
Форма оплаты заказа.

Валидация двухуровневая: HTML-атрибуты (required, pattern, min/max, type)
дают мгновенную проверку в браузере, серверные clean_* повторяют её —
браузерные ограничения обходятся, поэтому доверять им нельзя.
"""
from __future__ import annotations

import re
from datetime import date

from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import PromoCode

CARD_NUMBER_RE = re.compile(r"^\d{4} ?\d{4} ?\d{4} ?\d{4}$")
PHONE_RE = re.compile(r"^\+375 ?\(?(25|29|33|44)\)? ?\d{3}-?\d{2}-?\d{2}$")


class PaymentForm(forms.Form):
    """Поля страницы оплаты: контакты, доставка, способ оплаты, карта, промокод."""

    promo: PromoCode | None = None

    PAYMENT_CHOICES = (
        ("CARD", _("Банковская карта")),
        ("ERIP", _("ЕРИП / Расчёт")),
        ("CASH", _("Наличными при получении")),
    )
    DELIVERY_CHOICES = (
        ("PICKUP", _("Самовывоз из аптеки")),
        ("COURIER", _("Курьером по городу")),
        ("POST", _("Почтовая доставка")),
    )

    full_name = forms.CharField(
        label=_("Получатель"),
        max_length=120,
        min_length=5,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Иванов Иван Иванович",
                "autocomplete": "name",
                "spellcheck": "false",
                "autocapitalize": "words",
            }
        ),
    )
    email = forms.EmailField(
        label=_("Электронная почта"),
        widget=forms.EmailInput(
            attrs={"placeholder": "client@example.by", "autocomplete": "email", "inputmode": "email"}
        ),
    )
    phone = forms.CharField(
        label=_("Телефон"),
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "type": "tel",
                "placeholder": "+375 (29) 700-10-01",
                "pattern": r"\+375 ?\(?(25|29|33|44)\)? ?\d{3}-?\d{2}-?\d{2}",
                "autocomplete": "tel",
                "inputmode": "tel",
            }
        ),
        help_text=_("Формат: +375 (29) 700-10-01"),
    )
    delivery_method = forms.ChoiceField(
        label=_("Способ получения"),
        choices=DELIVERY_CHOICES,
        initial="PICKUP",
        widget=forms.RadioSelect,
    )
    city = forms.CharField(
        label=_("Город"),
        max_length=120,
        initial="Минск",
        widget=forms.TextInput(attrs={"list": "city-options", "autocomplete": "address-level2"}),
    )
    address = forms.CharField(
        label=_("Адрес доставки"),
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={"autocomplete": "address-line1"}),
        help_text=_("Обязателен для курьерской и почтовой доставки."),
    )
    delivery_date = forms.DateField(
        label=_("Желаемая дата получения"),
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    delivery_time = forms.TimeField(
        label=_("Удобное время"),
        required=False,
        widget=forms.TimeInput(attrs={"type": "time", "step": "1800"}),
    )
    payment_method = forms.ChoiceField(
        label=_("Способ оплаты"),
        choices=PAYMENT_CHOICES,
        initial="CARD",
    )
    card_number = forms.CharField(
        label=_("Номер карты"),
        required=False,
        max_length=19,
        widget=forms.TextInput(
            attrs={
                "placeholder": "4500 1234 5678 9010",
                "pattern": r"\d{4} ?\d{4} ?\d{4} ?\d{4}",
                "autocomplete": "cc-number",
                "inputmode": "numeric",
            }
        ),
    )
    card_holder = forms.CharField(
        label=_("Имя на карте"),
        required=False,
        max_length=120,
        widget=forms.TextInput(
            attrs={"placeholder": "IVAN IVANOV", "autocomplete": "cc-name", "spellcheck": "false"}
        ),
    )
    card_expiry = forms.CharField(
        label=_("Срок действия"),
        required=False,
        widget=forms.TextInput(attrs={"type": "month", "autocomplete": "cc-exp"}),
    )
    card_cvc = forms.CharField(
        label=_("CVC/CVV"),
        required=False,
        max_length=4,
        widget=forms.TextInput(
            attrs={
                "pattern": r"\d{3,4}",
                "inputmode": "numeric",
                "autocomplete": "cc-csc",
                "placeholder": "123",
                "size": "4",
            }
        ),
    )
    promo_code = forms.CharField(
        label=_("Промокод"),
        required=False,
        max_length=32,
        widget=forms.TextInput(
            attrs={
                "placeholder": "VITAMIN15",
                "list": "promo-list",
                "autocapitalize": "characters",
                "spellcheck": "false",
                "autocomplete": "off",
            }
        ),
    )
    bonus_points = forms.IntegerField(
        label=_("Списать бонусов"),
        required=False,
        min_value=0,
        max_value=500,
        initial=0,
        widget=forms.NumberInput(attrs={"type": "range", "step": "50"}),
    )
    comment = forms.CharField(
        label=_("Комментарий к заказу"),
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={"rows": 3, "maxlength": 500}),
    )
    need_receipt = forms.BooleanField(label=_("Прислать электронный чек"), required=False, initial=True)
    accept_policy = forms.BooleanField(
        label=_("Согласен с политикой конфиденциальности"),
        error_messages={"required": _("Без согласия оплата невозможна.")},
    )

    def clean_phone(self) -> str:
        phone = (self.cleaned_data.get("phone") or "").strip()
        if not PHONE_RE.match(phone):
            raise forms.ValidationError(_("Введите белорусский мобильный: +375 (29) 700-10-01."))
        return phone

    def clean_delivery_date(self) -> date:
        value: date = self.cleaned_data["delivery_date"]
        today = timezone.localdate()
        if value < today:
            raise forms.ValidationError(_("Дата получения не может быть в прошлом."))
        if (value - today).days > 30:
            raise forms.ValidationError(_("Заказ оформляется не более чем на 30 дней вперёд."))
        return value

    def clean_promo_code(self) -> str:
        code = (self.cleaned_data.get("promo_code") or "").strip().upper()
        if not code:
            return ""
        promo = PromoCode.objects.filter(code__iexact=code).first()
        if promo is None or not promo.is_current():
            raise forms.ValidationError(_("Промокод не найден или срок его действия истёк."))
        self.promo = promo
        return code

    def clean(self) -> dict[str, object]:
        """Межполевые правила: карта нужна только для CARD, адрес — для доставки."""
        cleaned = super().clean()
        if cleaned.get("delivery_method") in {"COURIER", "POST"} and not cleaned.get("address"):
            self.add_error("address", _("Укажите адрес для выбранного способа доставки."))
        if cleaned.get("payment_method") == "CARD":
            if not CARD_NUMBER_RE.match((cleaned.get("card_number") or "").strip()):
                self.add_error("card_number", _("Введите 16 цифр номера карты."))
            if not cleaned.get("card_holder"):
                self.add_error("card_holder", _("Укажите имя держателя карты."))
            if not cleaned.get("card_expiry"):
                self.add_error("card_expiry", _("Укажите срок действия карты."))
            if not re.fullmatch(r"\d{3,4}", (cleaned.get("card_cvc") or "").strip()):
                self.add_error("card_cvc", _("CVC — это 3 или 4 цифры."))
        return cleaned
