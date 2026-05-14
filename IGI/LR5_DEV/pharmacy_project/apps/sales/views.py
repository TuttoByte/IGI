"""Представления: только сборка форм и вызов selectors / SaleService."""
from __future__ import annotations

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.base import ContextMixin, TemplateResponseMixin

from apps.sales.forms import SaleHeaderForm, SaleLineFormSet
from apps.sales.models import Sale
from apps.sales import selectors as sale_selectors
from apps.sales.services import SaleLineInput, SaleService
from apps.accounts.mixins import DashboardAccessMixin


class SaleListView(DashboardAccessMixin, ListView):
    model = Sale
    template_name = "dashboard/sales/sale_list.html"
    context_object_name = "sales"
    paginate_by = 20

    def get_queryset(self):
        return sale_selectors.sales_for_list()


class SaleDetailView(DashboardAccessMixin, DetailView):
    model = Sale
    template_name = "dashboard/sales/sale_detail.html"
    context_object_name = "sale"
    pk_url_kwarg = "pk"

    def get_object(self, queryset=None):  # noqa: ARG002
        obj = sale_selectors.sale_by_pk_with_items(int(self.kwargs["pk"]))
        if obj is None:
            raise Http404()
        return obj


class SaleCreateView(DashboardAccessMixin, ContextMixin, TemplateResponseMixin, View):
    """GET/POST: шапка + formset; валидация и SaleService — единственное место сценария."""

    template_name = "dashboard/sales/sale_form.html"

    def get(self, request, *args: object, **kwargs: object) -> HttpResponse:
        context = self.get_context_data(
            header_form=SaleHeaderForm(),
            formset=SaleLineFormSet(prefix="items"),
        )
        return self.render_to_response(context)

    def post(self, request, *args: object, **kwargs: object) -> HttpResponse:
        header_form = SaleHeaderForm(request.POST)
        formset = SaleLineFormSet(request.POST, prefix="items")
        if header_form.is_valid() and formset.is_valid():
            return self._try_create(request, header_form, formset)
        return self.render_to_response(self.get_context_data(header_form=header_form, formset=formset))

    def _try_create(
        self,
        request,
        header_form: SaleHeaderForm,
        formset: SaleLineFormSet,
    ) -> HttpResponse:
        lines: list[SaleLineInput] = []
        for row in formset.cleaned_data:
            if not row or row.get("DELETE"):
                continue
            med = row.get("medication")
            qty = row.get("quantity")
            if med is not None and qty:
                lines.append(SaleLineInput(medication_id=int(med.pk), quantity=int(qty)))
        try:
            sale = SaleService.create_completed_sale(
                customer_id=int(header_form.cleaned_data["customer"].pk),
                employee_id=int(header_form.cleaned_data["employee"].pk),
                lines=tuple(lines),
            )
        except ValidationError as exc:
            for message in exc.messages:
                header_form.add_error(None, message)
            return self.render_to_response(
                self.get_context_data(header_form=header_form, formset=formset)
            )
        messages.success(request, _("Продажа оформлена."))
        return HttpResponseRedirect(sale.get_absolute_url())

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        ctx = super().get_context_data(**kwargs)
        ctx.setdefault("header_form", SaleHeaderForm())
        ctx.setdefault("formset", SaleLineFormSet(prefix="items"))
        return ctx
