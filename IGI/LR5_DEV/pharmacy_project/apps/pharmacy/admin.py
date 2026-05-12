"""
Админка: поисковые поля + select_related на списках, autocomplete для FK.

Тяжёлые списки препаратов не тянут category/department отдельными запросами на строку.
"""
from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.pharmacy.models import Category, Department, Medication


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "floor", "created_at")
    list_filter = ("floor",)
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "price",
        "quantity",
        "expiration_date",
        "requires_prescription",
        "category",
        "department",
        "created_at",
    )
    list_select_related = ("category", "department")
    list_filter = ("requires_prescription", "category", "department", "expiration_date")
    search_fields = ("name", "code", "slug", "manufacturer", "description")
    autocomplete_fields = ("category", "department")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "expiration_date"
    show_full_result_count = False

    fieldsets = (
        (None, {"fields": ("code", "name", "slug")}),
        (_("Описание"), {"fields": ("description", "instruction", "manufacturer", "image")}),
        (_("Склад и цена"), {"fields": ("price", "quantity", "expiration_date", "requires_prescription")}),
        (_("Классификация"), {"fields": ("category", "department")}),
        (_("Служебное"), {"fields": ("created_at", "updated_at")}),
    )
