"""Страницы клиента: только CUSTOMER, шаблоны под frontend/."""
from __future__ import annotations

from typing import Any

from django.views.generic import TemplateView

from apps.accounts.mixins import CabinetAccessMixin


class CabinetHomeView(CabinetAccessMixin, TemplateView):
    template_name = "frontend/cabinet/home.html"

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Кабинет"
        return ctx
