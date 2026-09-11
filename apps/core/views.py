from __future__ import annotations

from django.http import Http404
from django.shortcuts import render
from django.views.generic import DetailView, ListView, TemplateView

from apps.core import selectors
from apps.pharmacy import selectors as pharmacy_selectors


def home(request):
    """Главная: баннеры, каталог, анонс последней статьи и партнёры."""
    return render(
        request,
        "frontend/core/home.html",
        {
            "banners": selectors.active_banners(),
            "latest_article": selectors.latest_published_article(),
            "partners": selectors.active_partners(),
            "featured_medications": pharmacy_selectors.medications_for_catalog()[:6],
            "company": selectors.company_info(),
        },
    )


class NewsListView(ListView):
    """Публичная лента новостей аптеки."""

    template_name = "frontend/core/news_list.html"
    context_object_name = "articles"
    paginate_by = 9

    def get_queryset(self):
        return selectors.published_news()


class NewsDetailView(DetailView):
    """Публичная карточка новости."""

    template_name = "frontend/core/news_detail.html"
    context_object_name = "article"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_object(self, queryset=None):  # noqa: ARG002
        obj = selectors.news_by_slug(self.kwargs["slug"])
        if obj is None:
            raise Http404()
        return obj


class ContactsView(TemplateView):
    """Контакты сотрудников с фотографиями и текстовым графиком."""

    template_name = "frontend/core/contacts.html"

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        ctx = super().get_context_data(**kwargs)
        ctx["employees"] = selectors.active_employee_contacts()
        return ctx


class AboutView(TemplateView):
    """О компании: описание, видео, история по годам, реквизиты, сертификат."""

    template_name = "frontend/core/about.html"

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        ctx = super().get_context_data(**kwargs)
        company = selectors.company_info()
        milestones = list(company.milestones.all()) if company else []
        ctx["company"] = company
        ctx["milestones"] = milestones
        # Итоговая строка <tfoot> показывает показатели последнего года истории.
        ctx["last_milestone"] = milestones[-1] if milestones else None
        ctx["partners"] = selectors.active_partners()
        return ctx


class GlossaryView(TemplateView):
    """Словарь терминов: раскрывающиеся ответы + поиск по подстроке."""

    template_name = "frontend/core/glossary.html"

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        ctx = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()
        terms = selectors.published_glossary_terms()
        if query:
            terms = terms.filter(term__icontains=query) | terms.filter(question__icontains=query)
        ctx["query"] = query
        ctx["terms"] = terms.distinct()
        return ctx


class VacancyListView(ListView):
    """Список открытых вакансий с описанием и формой отклика."""

    template_name = "frontend/core/vacancies.html"
    context_object_name = "vacancies"

    def get_queryset(self):
        return selectors.open_vacancies()

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        ctx = super().get_context_data(**kwargs)
        ctx["applied_for"] = self.request.GET.get("applied", "")
        return ctx


class PromoCodeListView(TemplateView):
    """Промокоды и купоны: действующие и архив."""

    template_name = "frontend/core/promocodes.html"

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        ctx = super().get_context_data(**kwargs)
        ctx["current_promos"] = selectors.current_promo_codes()
        ctx["archived_promos"] = selectors.archived_promo_codes()
        return ctx


class PrivacyPolicyView(TemplateView):
    """Политика конфиденциальности аптечной сети."""

    template_name = "frontend/core/privacy.html"

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        ctx = super().get_context_data(**kwargs)
        ctx["company"] = selectors.company_info()
        return ctx
