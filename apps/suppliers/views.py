"""
CRUD на generic class-based views.

Список — FilterView (django-filter + пагинация из MultipleObjectMixin).
"""
from __future__ import annotations

from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django_filters.views import FilterView

from apps.suppliers.filters import SupplierFilter
from apps.suppliers.forms import SupplierForm
from apps.accounts.mixins import DashboardAccessMixin
from apps.suppliers.models import Supplier
from apps.suppliers import selectors as supplier_selectors
from apps.suppliers.services import SupplierService


class SupplierListView(DashboardAccessMixin, FilterView):
    filterset_class = SupplierFilter
    template_name = "dashboard/suppliers/supplier_list.html"
    paginate_by = 15
    context_object_name = "suppliers"

    def get_queryset(self):
        return supplier_selectors.suppliers_for_list()

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        ctx = super().get_context_data(**kwargs)
        q = self.request.GET.copy()
        q.pop("page", None)
        ctx["querystring"] = q.urlencode()
        return ctx


class SupplierDetailView(DashboardAccessMixin, DetailView):
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "dashboard/suppliers/supplier_detail.html"
    context_object_name = "supplier"

    def get_object(self, queryset=None):  # noqa: ARG002
        obj = supplier_selectors.supplier_by_slug_with_medications(self.kwargs["slug"])
        if obj is None:
            from django.http import Http404

            raise Http404()
        return obj


class SupplierCreateView(DashboardAccessMixin, CreateView):
    form_class = SupplierForm
    template_name = "dashboard/suppliers/supplier_form.html"

    def form_valid(self, form: SupplierForm) -> HttpResponse:
        self.object = SupplierService.save_from_form(form)
        messages.success(self.request, _("Поставщик создан."))
        return HttpResponseRedirect(self.object.get_absolute_url())


class SupplierUpdateView(DashboardAccessMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "dashboard/suppliers/supplier_form.html"
    context_object_name = "supplier"

    def get_queryset(self):
        return supplier_selectors.supplier_queryset_for_crud()

    def form_valid(self, form: SupplierForm) -> HttpResponse:
        SupplierService.save_from_form(form)
        messages.success(self.request, _("Изменения сохранены."))
        return HttpResponseRedirect(self.get_object().get_absolute_url())


class SupplierDeleteView(DashboardAccessMixin, DeleteView):
    model = Supplier
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "dashboard/suppliers/supplier_confirm_delete.html"
    success_url = reverse_lazy("suppliers:supplier_list")

    def delete(self, request, *args: object, **kwargs: object) -> HttpResponse:
        obj = self.get_object()
        SupplierService.delete(obj)
        messages.success(request, _("Поставщик удалён."))
        return HttpResponseRedirect(self.success_url)
