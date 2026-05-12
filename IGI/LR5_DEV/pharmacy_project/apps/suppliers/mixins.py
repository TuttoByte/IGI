"""Доступ к CRUD поставщиков только у staff (админка аптеки)."""
from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Минимальная политика для внутренних операций (можно заменить на роль EMPLOYEE)."""

    def test_func(self) -> bool:
        user = self.request.user
        return bool(user.is_authenticated and user.is_staff)
