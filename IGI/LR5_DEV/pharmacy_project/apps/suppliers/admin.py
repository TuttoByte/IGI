"""Админка поставщиков: поиск по названию, удобный выбор M2M препаратов."""
from __future__ import annotations

from django.contrib import admin
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from apps.suppliers.models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "email", "contract_number", "medication_count_display", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "slug", "email", "contract_number", "phone")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("medications",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("name", "slug", "contract_number")}),
        (_("Контакты"), {"fields": ("email", "phone", "address")}),
        (_("Препараты"), {"fields": ("medications",)}),
        (_("Служебное"), {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description=_("препаратов"))
    def medication_count_display(self, obj: Supplier) -> int:
        return int(getattr(obj, "medication_count", 0))

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(medication_count=Count("medications", distinct=True))
