"""Админка модерации: фильтры по статусу, препарату, оценке."""
from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.reviews.models import Review, ReviewModerationStatus


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "moderation_status", "rating", "user", "medication", "text_preview")
    list_filter = ("moderation_status", "rating", "created_at", "medication__category")
    search_fields = ("user__username", "medication__name", "medication__code", "text")
    list_select_related = ("user", "medication")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("user", "medication")
    ordering = ("-created_at",)
    actions = ("approve_reviews", "reject_reviews")

    @admin.display(description=_("текст"))
    def text_preview(self, obj: Review) -> str:
        t = (obj.text or "").strip()
        return (t[:80] + "…") if len(t) > 80 else (t or "—")

    @admin.action(description=_("Опубликовать выбранные"))
    def approve_reviews(self, request, queryset):
        queryset.update(moderation_status=ReviewModerationStatus.APPROVED)

    @admin.action(description=_("Отклонить выбранные"))
    def reject_reviews(self, request, queryset):
        queryset.update(moderation_status=ReviewModerationStatus.REJECTED)
