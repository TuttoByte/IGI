"""RBAC-миксины для CBV: панель сотрудников и личный кабинет клиента — разные зоны."""
from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

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
    Только CUSTOMER — зона /cabinet/, шаблоны templates/frontend/cabinet/.
    """

    login_url = reverse_lazy("accounts:login")

    def test_func(self) -> bool:
        user = self.request.user
        if not user.is_authenticated:
            return False
        return getattr(user, "role", None) == UserRole.CUSTOMER

    def handle_no_permission(self):
        """Гость → логин; не-клиент → 403 (не смешиваем с dashboard)."""
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        from django.core.exceptions import PermissionDenied

        raise PermissionDenied(_("Раздел только для клиентов."))
