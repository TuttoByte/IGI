"""Личный кабинет: доступен всем авторизованным пользователям."""
from __future__ import annotations

import calendar
from datetime import date
from typing import Any

from django.views.generic import TemplateView

from apps.accounts.mixins import CabinetAccessMixin

MONTHS_RU = {
    1: "Январь",
    2: "Февраль",
    3: "Март",
    4: "Апрель",
    5: "Май",
    6: "Июнь",
    7: "Июль",
    8: "Август",
    9: "Сентябрь",
    10: "Октябрь",
    11: "Ноябрь",
    12: "Декабрь",
}
WEEKDAYS_RU = ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс")


class CabinetHomeView(CabinetAccessMixin, TemplateView):
    template_name = "frontend/cabinet/home.html"

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        profile = getattr(self.request.user, "profile", None)
        ctx["page_title"] = "Кабинет"
        ctx["profile"] = profile
        ctx["birth_calendar"] = self._format_birth_calendar(profile.birth_date) if profile else ""
        return ctx

    @staticmethod
    def _format_birth_calendar(birth_date: date) -> str:
        month_days = calendar.Calendar(firstweekday=calendar.MONDAY).monthdayscalendar(
            birth_date.year,
            birth_date.month,
        )
        rows = [
            f"{MONTHS_RU[birth_date.month]} {birth_date.year}".center(28).rstrip(),
            "".join(day.center(4) for day in WEEKDAYS_RU).rstrip(),
        ]
        for week in month_days:
            cells = []
            for day in week:
                if not day:
                    cells.append("    ")
                elif day == birth_date.day:
                    cells.append(f"[{day:02d}]")
                else:
                    cells.append(f"{day:>2}  ")
            rows.append("".join(cells).rstrip())
        return "\n".join(rows)
