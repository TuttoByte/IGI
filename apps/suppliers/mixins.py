"""Обратная совместимость: используйте apps.accounts.mixins.DashboardAccessMixin."""
from __future__ import annotations

from apps.accounts.mixins import DashboardAccessMixin

StaffRequiredMixin = DashboardAccessMixin
