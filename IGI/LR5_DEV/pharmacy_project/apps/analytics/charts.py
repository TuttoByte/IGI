"""PNG-графики аналитики, сгенерированные на сервере через matplotlib."""
from __future__ import annotations

import base64
import os
import tempfile
import warnings
from io import BytesIO

from apps.analytics.selectors import DepartmentRevenueRow, SalesByDayRow


def _pyplot():
    os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "matplotlib-cache"))
    os.environ.setdefault("XDG_CACHE_HOME", tempfile.gettempdir())
    warnings.filterwarnings("ignore", message="Unable to import Axes3D.*", category=UserWarning)
    # Import lazily so Django can start even if chart rendering is unavailable.
    import matplotlib

    matplotlib.use("Agg")
    from matplotlib import pyplot as plt

    return plt


def _figure_to_data_uri(plt) -> str:
    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format="png", dpi=130, bbox_inches="tight")
    plt.close()
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def sales_by_day_png(rows: list[SalesByDayRow]) -> str:
    if not rows:
        return ""
    try:
        plt = _pyplot()
    except Exception:
        return ""

    labels = [r.day.strftime("%d.%m") for r in rows]
    revenue = [float(r.revenue) for r in rows]
    x_values = list(range(len(labels)))

    plt.figure(figsize=(7.2, 3.2))
    plt.plot(x_values, revenue, marker="o", linewidth=2, color="#0b57d0")
    plt.fill_between(x_values, revenue, color="#0b57d0", alpha=0.08)
    plt.title("Выручка по дням")
    plt.xlabel("Дата")
    plt.ylabel("BYN")
    plt.grid(axis="y", alpha=0.25)
    plt.xticks(x_values, labels, rotation=35, ha="right")
    return _figure_to_data_uri(plt)


def revenue_by_department_png(rows: list[DepartmentRevenueRow]) -> str:
    if not rows:
        return ""
    try:
        plt = _pyplot()
    except Exception:
        return ""

    labels = [r.department_name for r in rows]
    revenue = [float(r.revenue) for r in rows]
    x_values = list(range(len(labels)))

    plt.figure(figsize=(7.2, 3.2))
    plt.bar(x_values, revenue, color="#198754")
    plt.title("Выручка по отделам")
    plt.xlabel("Отдел")
    plt.ylabel("BYN")
    plt.grid(axis="y", alpha=0.25)
    plt.xticks(x_values, labels, rotation=25, ha="right")
    return _figure_to_data_uri(plt)
