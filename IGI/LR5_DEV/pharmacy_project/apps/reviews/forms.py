"""Формы отзывов: только поля, без ORM-сценариев."""
from __future__ import annotations

from django import forms

from apps.reviews.models import Review


class ReviewCreateForm(forms.Form):
    rating = forms.IntegerField(label="Оценка", min_value=1, max_value=5)
    text = forms.CharField(label="Текст", required=False, widget=forms.Textarea(attrs={"rows": 5}))


class ReviewUpdateForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "text")
        widgets = {"text": forms.Textarea(attrs={"rows": 5})}
