"""
Селекторы аналитики: только ORM (aggregate / annotate / values), без raw SQL.

Запросы сгруппированы по смыслу; каждая функция — один проход к БД или явный
набор независимых запросов без N+1 в циклах по строкам продаж.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any

from django.db.models import Avg, Count, DecimalField, IntegerField, Q, Sum, Value
from django.db.models.functions import Coalesce, TruncDate
from django.utils import timezone

from apps.sales.models import Sale, SaleItem, SaleStatus


def _completed_sales_filter() -> Q:
    return Q(status=SaleStatus.COMPLETED)


@dataclass(frozen=True)
class PharmacyAnalyticsSummary:
    """Итоги по проведённым продажам (один aggregate по Sale)."""

    total_revenue: Decimal
    completed_sales_count: int
    average_check: Decimal | None


def pharmacy_analytics_summary() -> PharmacyAnalyticsSummary:
    agg = Sale.objects.filter(_completed_sales_filter()).aggregate(
        total_revenue=Coalesce(
            Sum("total_price"),
            Value(Decimal("0.00")),
            output_field=DecimalField(max_digits=14, decimal_places=2),
        ),
        completed_sales_count=Count("id"),
        average_check=Avg("total_price"),
    )
    count = int(agg["completed_sales_count"] or 0)
    total = agg["total_revenue"]
    assert isinstance(total, Decimal)
    avg = agg["average_check"]
    avg_dec: Decimal | None
    if avg is None:
        avg_dec = None
    elif isinstance(avg, Decimal):
        avg_dec = avg
    else:
        avg_dec = Decimal(str(avg))
    return PharmacyAnalyticsSummary(
        total_revenue=total,
        completed_sales_count=count,
        average_check=avg_dec,
    )


@dataclass(frozen=True)
class DepartmentRevenueRow:
    department_id: int
    department_name: str
    revenue: Decimal
    line_count: int


def pharmacy_revenue_by_department() -> list[DepartmentRevenueRow]:
    """
    Выручка по отделам: группировка строк SaleItem → препарат → отдел.

    Один запрос с GROUP BY (через values + annotate).
    """
    qs = (
        SaleItem.objects.filter(sale__status=SaleStatus.COMPLETED)
        .values("medication__department_id", "medication__department__name")
        .annotate(
            revenue=Coalesce(
                Sum("subtotal"),
                Value(Decimal("0.00")),
                output_field=DecimalField(max_digits=14, decimal_places=2),
            ),
            line_count=Count("id"),
        )
        .order_by("-revenue", "medication__department__name")
    )
    rows: list[DepartmentRevenueRow] = []
    for row in qs:
        did = row["medication__department_id"]
        if did is None:
            continue
        rev = row["revenue"]
        assert isinstance(rev, Decimal)
        rows.append(
            DepartmentRevenueRow(
                department_id=int(did),
                department_name=str(row["medication__department__name"] or ""),
                revenue=rev,
                line_count=int(row["line_count"] or 0),
            )
        )
    return rows


@dataclass(frozen=True)
class PopularMedicationRow:
    medication_id: int
    medication_name: str
    medication_code: str
    units_sold: int
    revenue: Decimal
    sale_lines: int


def pharmacy_popular_medications(*, limit: int = 10) -> list[PopularMedicationRow]:
    """Популярные препараты по сумме проданных единиц (Sum quantity), один запрос с LIMIT."""
    lim = max(1, min(limit, 100))
    qs = (
        SaleItem.objects.filter(sale__status=SaleStatus.COMPLETED)
        .values("medication_id", "medication__name", "medication__code")
        .annotate(
            units_sold=Coalesce(Sum("quantity"), Value(0), output_field=IntegerField()),
            revenue=Coalesce(
                Sum("subtotal"),
                Value(Decimal("0.00")),
                output_field=DecimalField(max_digits=14, decimal_places=2),
            ),
            sale_lines=Count("id"),
        )
        .order_by("-units_sold", "-revenue")[:lim]
    )
    out: list[PopularMedicationRow] = []
    for row in qs:
        mid = row["medication_id"]
        if mid is None:
            continue
        rev = row["revenue"]
        assert isinstance(rev, Decimal)
        out.append(
            PopularMedicationRow(
                medication_id=int(mid),
                medication_name=str(row["medication__name"] or ""),
                medication_code=str(row["medication__code"] or ""),
                units_sold=int(row["units_sold"] or 0),
                revenue=rev,
                sale_lines=int(row["sale_lines"] or 0),
            )
        )
    return out


@dataclass(frozen=True)
class SalesByDayRow:
    day: date
    revenue: Decimal
    sale_count: int


def pharmacy_sales_by_day(*, days: int = 30) -> list[SalesByDayRow]:
    """
    Продажи по календарным дням: TruncDate + Sum + Count по проведённым чекам.

    Один запрос с группировкой по дню (UTC/активная TZ — как в Django ORM).
    """
    n = max(1, min(days, 366))
    end = timezone.now()
    start = end - timedelta(days=n)
    qs = (
        Sale.objects.filter(_completed_sales_filter(), created_at__gte=start, created_at__lte=end)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(
            revenue=Coalesce(
                Sum("total_price"),
                Value(Decimal("0.00")),
                output_field=DecimalField(max_digits=14, decimal_places=2),
            ),
            sale_count=Count("id"),
        )
        .order_by("day")
    )
    out: list[SalesByDayRow] = []
    for row in qs:
        d = row["day"]
        if isinstance(d, datetime):
            day_val = d.date()
        elif isinstance(d, date):
            day_val = d
        else:
            continue
        rev = row["revenue"]
        assert isinstance(rev, Decimal)
        out.append(
            SalesByDayRow(
                day=day_val,
                revenue=rev,
                sale_count=int(row["sale_count"] or 0),
            )
        )
    return out


def chart_payload_by_day(rows: list[SalesByDayRow]) -> dict[str, Any]:
    """Сериализация рядов в простые JSON-совместимые структуры."""
    return {
        "labels": [r.day.isoformat() for r in rows],
        "revenue": [float(r.revenue) for r in rows],
        "sale_count": [r.sale_count for r in rows],
    }


def chart_payload_by_department(rows: list[DepartmentRevenueRow]) -> dict[str, Any]:
    return {
        "labels": [r.department_name for r in rows],
        "revenue": [float(r.revenue) for r in rows],
    }
