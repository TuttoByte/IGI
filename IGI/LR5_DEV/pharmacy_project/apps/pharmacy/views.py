"""
Каталог и карточки: только HTTP + вызовы selectors / FilterSet.

Фильтрация и сортировка целиком в MedicationFilter; queryset из selectors.
"""
from __future__ import annotations

from django.views.generic import DetailView
from django_filters.views import FilterView

from apps.pharmacy.filters import MedicationFilter
from apps.pharmacy import selectors
from apps.reviews import selectors as review_selectors
from apps.reviews.models import Review


class MedicationListView(FilterView):
    """Список препаратов: django-filter + пагинация из MultipleObjectMixin."""

    filterset_class = MedicationFilter
    template_name = "frontend/pharmacy/medication_list.html"
    paginate_by = 20
    context_object_name = "medications"

    def get_queryset(self):
        return selectors.medications_for_catalog()

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        ctx = super().get_context_data(**kwargs)
        q = self.request.GET.copy()
        q.pop("page", None)
        ctx["querystring"] = q.urlencode()
        return ctx


class MedicationDetailView(DetailView):
    """Карточка препарата: queryset уже с select_related из селектора."""

    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "frontend/pharmacy/medication_detail.html"
    context_object_name = "medication"

    def get_queryset(self):
        return selectors.medications_for_catalog()

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        ctx = super().get_context_data(**kwargs)
        med = self.object
        ctx["review_stats"] = review_selectors.medication_review_stats(med.pk)
        ctx["latest_reviews"] = review_selectors.approved_reviews_for_medication(med.pk, limit=12)
        if self.request.user.is_authenticated:
            ctx["user_review"] = (
                Review.objects.filter(medication_id=med.pk, user_id=self.request.user.pk)
                .only("pk", "moderation_status")
                .first()
            )
        else:
            ctx["user_review"] = None
        return ctx


class CategoryDetailView(DetailView):
    """Категория с префетчем препаратов (prefetch_related в селекторе)."""

    template_name = "frontend/pharmacy/category_detail.html"
    context_object_name = "category"

    def get_object(self, queryset=None):  # noqa: ARG002
        obj = selectors.category_detail_with_medications(self.kwargs["slug"])
        if obj is None:
            from django.http import Http404

            raise Http404()
        return obj


class DepartmentDetailView(DetailView):
    template_name = "frontend/pharmacy/department_detail.html"
    context_object_name = "department"

    def get_object(self, queryset=None):  # noqa: ARG002
        obj = selectors.department_detail_with_medications(self.kwargs["slug"])
        if obj is None:
            from django.http import Http404

            raise Http404()
        return obj
