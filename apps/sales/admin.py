"""Админка: просмотр чеков; создание только через UI (инварианты в SaleService)."""
from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.sales.models import Sale, SaleItem


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ("medication", "quantity", "price", "subtotal")
    can_delete = False

    def has_add_permission(self, request, obj=None) -> bool:
        return False


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "status", "customer", "employee", "total_price")
    list_filter = ("status", "created_at")
    search_fields = ("customer__username", "employee__username")
    readonly_fields = ("created_at", "total_price", "customer", "employee", "status")
    inlines = (SaleItemInline,)

    def has_add_permission(self, request) -> bool:
        return False


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ("sale", "medication", "quantity", "price", "subtotal")

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False
