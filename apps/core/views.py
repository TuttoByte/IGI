from __future__ import annotations

from django.http import Http404
from django.shortcuts import render
from django.views.generic import DetailView, ListView, TemplateView

from apps.core import selectors


def home(request):
    return render(request, "frontend/core/home.html")


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
