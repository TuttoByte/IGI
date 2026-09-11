"""Формы отзывов: только поля, без ORM-сценариев."""
from __future__ import annotations

from django import forms

from apps.pharmacy.models import Medication
from apps.reviews.models import Review

RATING_CHOICES = (
    (5, "5 — отлично"),
    (4, "4 — хорошо"),
    (3, "3 — нормально"),
    (2, "2 — плохо"),
    (1, "1 — очень плохо"),
)


class ReviewCreateForm(forms.Form):
    """Отзыв на заранее выбранный препарат (переход из карточки товара)."""

    rating = forms.TypedChoiceField(
        label="Оценка",
        choices=RATING_CHOICES,
        coerce=int,
        widget=forms.RadioSelect,
    )
    text = forms.CharField(
        label="Текст отзыва",
        required=False,
        max_length=2000,
        widget=forms.Textarea(attrs={"rows": 5, "maxlength": 2000, "placeholder": "Что понравилось, что нет"}),
    )


class ReviewCreateAnyForm(ReviewCreateForm):
    """Отзыв со страницы «Отзывы»: препарат выбирается выпадающим списком."""

    medication = forms.ModelChoiceField(
        label="Препарат",
        queryset=Medication.objects.order_by("name"),
        empty_label="— выберите препарат —",
    )

    field_order = ("medication", "rating", "text")


class ReviewUpdateForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "text")
        widgets = {"text": forms.Textarea(attrs={"rows": 5})}
