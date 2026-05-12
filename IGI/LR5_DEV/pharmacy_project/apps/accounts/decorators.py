"""
Декораторы доступа по роли.

Для CBV навешиваем через django.utils.decorators.method_decorator(..., name="dispatch").
В этом режиме Django передаёт в обёртку уже «связанный» dispatch: первый аргумент —
HttpRequest (self зашит в partial), поэтому сигнатура декоратора — (request, *args).
"""
from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponseBase
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import UserRole


def role_required(
    *roles: UserRole | str,
) -> Callable[[Callable[..., HttpResponseBase]], Callable[..., HttpResponseBase]]:
    """
    Декоратор для dispatch CBV (через method_decorator).

    Неаутентифицированный пользователь уходит на LOGIN_URL; чужая роль — 403.
    """
    allowed = {r if isinstance(r, str) else r.value for r in roles}

    def decorator(view_func: Callable[..., HttpResponseBase]) -> Callable[..., HttpResponseBase]:
        @wraps(view_func)
        def _wrapped(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
            if not request.user.is_authenticated:
                return redirect_to_login(
                    next=request.get_full_path(),
                    login_url=getattr(settings, "LOGIN_URL", "/accounts/login/"),
                )
            role = getattr(request.user, "role", None)
            if role not in allowed:
                raise PermissionDenied(_("Недостаточно прав."))
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
