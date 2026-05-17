"""Дашборд аналитики: только сборка контекста из selectors."""
from __future__ import annotations

from typing import Any

from django.views.generic import TemplateView

from apps.analytics import charts as analytics_charts
from apps.analytics import selectors as analytics_selectors
from apps.accounts.mixins import DashboardAccessMixin


class PharmacyAnalyticsDashboardView(DashboardAccessMixin, TemplateView):
    template_name = "dashboard/analytics/dashboard.html"

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        summary = analytics_selectors.pharmacy_analytics_summary()
        by_department = analytics_selectors.pharmacy_revenue_by_department()
        popular = analytics_selectors.pharmacy_popular_medications(limit=10)
        by_day = analytics_selectors.pharmacy_sales_by_day(days=30)
        ctx["summary"] = summary
        ctx["by_department"] = by_department
        ctx["popular"] = popular
        ctx["by_day"] = by_day
        ctx["sales_by_day_chart"] = analytics_charts.sales_by_day_png(by_day)
        ctx["department_revenue_chart"] = analytics_charts.revenue_by_department_png(by_department)
        return ctx
