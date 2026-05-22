"""RBAC-миксины для CBV: панель сотрудников и личный кабинет — разные зоны."""
from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy

from apps.accounts.models import UserRole


class DashboardAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Только ADMIN и EMPLOYEE — зона /dashboard/, шаблоны templates/dashboard/.
    Не использовать на публичных или клиентских страницах.
    """

    login_url = reverse_lazy("accounts:login")

    def test_func(self) -> bool:
        user = self.request.user
        if not user.is_authenticated:
            return False
        role = getattr(user, "role", None)
        return role in (UserRole.ADMIN, UserRole.EMPLOYEE)


class CabinetAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Любой авторизованный пользователь — зона /cabinet/.
    Ролевые рабочие инструменты остаются в /dashboard/.
    """

    login_url = reverse_lazy("accounts:login")

    def test_func(self) -> bool:
        return self.request.user.is_authenticated
