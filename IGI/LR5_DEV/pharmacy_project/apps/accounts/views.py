"""
Представления только на CBV: FormView / встроенные LoginView / LogoutView.

Бизнес-сценарии не реализуются здесь — только HTTP-адаптация и вызов services.
"""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView

from apps.accounts.decorators import role_required
from apps.accounts.forms import CustomerRegistrationForm, StyledAuthenticationForm
from apps.accounts.models import UserRole
from apps.accounts.services import CustomerRegistrationDTO, RegistrationService


class RegisterView(FormView):
    """Регистрация клиента: форма → DTO → RegistrationService."""

    template_name = "accounts/register.html"
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form: CustomerRegistrationForm) -> HttpResponse:
        dto = CustomerRegistrationDTO(
            username=form.cleaned_data["username"],
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password1"],
            birth_date=form.cleaned_data["birth_date"],
            phone=form.cleaned_data["phone"],
            address=form.cleaned_data["address"],
            avatar=form.cleaned_data.get("avatar"),
        )
        RegistrationService.register_customer(dto)
        messages.success(self.request, _("Регистрация успешна. Войдите в систему."))
        return super().form_valid(form)


class AccountLoginView(LoginView):
    """Стандартный LoginView — не дублируем аутентификацию вручную."""

    template_name = "accounts/login.html"
    redirect_authenticated_user = True
    authentication_form = StyledAuthenticationForm


class AccountLogoutView(LogoutView):
    """POST-logout (Django 5); в шаблоне используем форму с csrf."""

    next_page = reverse_lazy("core:home")


@method_decorator(role_required(UserRole.ADMIN), name="dispatch")
class AdminDashboardView(TemplateView):
    """
    Пример RBAC на CBV: доступ только у ADMIN.

    EMPLOYEE/CUSTOMER получат 403; неаутентифицированный — редирект на LOGIN_URL.
    """

    template_name = "accounts/admin_dashboard.html"

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = _("Панель администратора")
        return ctx


@method_decorator(role_required(UserRole.ADMIN, UserRole.EMPLOYEE), name="dispatch")
class StaffDashboardView(TemplateView):
    """Зона сотрудников: ADMIN и EMPLOYEE (ролевой надмножество)."""

    template_name = "accounts/staff_dashboard.html"

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = _("Панель сотрудника")
        return ctx
