from django.contrib import admin

from apps.core.models import (
    Banner,
    CompanyInfo,
    CompanyMilestone,
    EmployeeContact,
    GlossaryTerm,
    NewsArticle,
    Partner,
    PromoCode,
    Vacancy,
)


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


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "subtitle", "sort_order", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title", "subtitle", "alt_text")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "site_url", "cooperation_since", "sort_order", "is_active")
    list_filter = ("is_active", "country")
    search_fields = ("name", "description", "site_url", "slug")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")


class CompanyMilestoneInline(admin.TabularInline):
    model = CompanyMilestone
    extra = 1


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ("name", "legal_name", "founded_year", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "legal_name", "about_text", "requisites", "certificate_number")
    readonly_fields = ("created_at", "updated_at")
    inlines = (CompanyMilestoneInline,)


@admin.register(GlossaryTerm)
class GlossaryTermAdmin(admin.ModelAdmin):
    list_display = ("term", "abbreviation", "question", "added_at", "sort_order", "is_published")
    list_filter = ("is_published", "added_at")
    search_fields = ("term", "abbreviation", "question", "short_answer", "answer", "slug")
    prepopulated_fields = {"slug": ("term",)}
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "added_at"


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ("title", "city", "employment_type", "salary_from", "salary_to", "is_open")
    list_filter = ("is_open", "employment_type", "city")
    search_fields = ("title", "description", "responsibilities", "requirements", "slug")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "published_at"


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "discount_percent", "valid_from", "valid_to", "is_active")
    list_filter = ("is_active", "valid_from", "valid_to")
    search_fields = ("code", "title", "description")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "valid_to"
