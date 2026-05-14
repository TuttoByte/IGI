"""Точка входа в панель: отдельные от публичного сайта шаблоны и навигация."""
from __future__ import annotations

from typing import Any

from django.views.generic import TemplateView

from apps.accounts.mixins import DashboardAccessMixin


class DashboardIndexView(DashboardAccessMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Панель"
        return ctx
