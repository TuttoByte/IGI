from django.contrib import admin

from apps.core.models import EmployeeContact, NewsArticle


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "published_at", "is_published", "created_at")
    list_filter = ("is_published", "published_at")
    search_fields = ("title", "lead", "content", "slug")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "published_at"


@admin.register(EmployeeContact)
class EmployeeContactAdmin(admin.ModelAdmin):
    list_display = ("full_name", "position", "phone", "email", "sort_order", "is_active")
    list_filter = ("is_active", "position")
    search_fields = ("full_name", "position", "phone", "email", "work_calendar", "note", "slug")
    prepopulated_fields = {"slug": ("full_name",)}
    readonly_fields = ("created_at", "updated_at")
