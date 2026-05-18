"""
Представления только на CBV: FormView / встроенные LoginView / LogoutView.

Панель сотрудников вынесена в apps.dashboard — здесь только публичные auth-страницы.
"""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, RedirectView

from apps.accounts.forms import CustomerRegistrationForm, StyledAuthenticationForm
from apps.accounts.services import CustomerRegistrationDTO, RegistrationService


class RegisterView(FormView):
    """Регистрация клиента: форма → DTO → RegistrationService."""

    template_name = "frontend/accounts/register.html"
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form: CustomerRegistrationForm) -> HttpResponse:
        dto = CustomerRegistrationDTO(
            username=form.cleaned_data["username"],
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password1"],
            birth_date=form.cleaned_data["birth_date"],
            phone=form.cleaned_data["phone"],
            timezone=form.cleaned_data["timezone"],
            address=form.cleaned_data["address"],
            avatar=form.cleaned_data.get("avatar"),
        )
        RegistrationService.register_customer(dto)
        messages.success(self.request, _("Регистрация успешна. Войдите в систему."))
        return super().form_valid(form)


class AccountLoginView(LoginView):
    """Стандартный LoginView — не дублируем аутентификацию вручную."""

    template_name = "frontend/accounts/login.html"
    redirect_authenticated_user = True
    authentication_form = StyledAuthenticationForm


class AccountLogoutView(LogoutView):
    """POST-logout (Django 5); в шаблоне используем форму с csrf."""

    next_page = reverse_lazy("core:home")


class LegacyPortalRedirectView(RedirectView):
    """Старые URL ведут в единую панель /dashboard/ (доступ проверяется там)."""

    pattern_name = "dashboard:index"
    permanent = False
