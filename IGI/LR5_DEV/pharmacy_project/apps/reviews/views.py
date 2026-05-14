"""CBV: список/деталь/создание/редактирование/удаление; сценарии — в services/selectors."""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, DetailView, FormView, UpdateView
from django_filters.views import FilterView

from apps.pharmacy.models import Medication
from apps.reviews.filters import ReviewFilter
from apps.reviews.forms import ReviewCreateForm, ReviewUpdateForm
from apps.reviews.models import Review
from apps.reviews import selectors as review_selectors
from apps.reviews.services import ReviewService

_REVIEW_LOGIN_URL = reverse_lazy("accounts:login")


class ReviewListView(FilterView):
    filterset_class = ReviewFilter
    template_name = "frontend/reviews/review_list.html"
    paginate_by = 20
    context_object_name = "reviews"

    def get_queryset(self):
        return review_selectors.reviews_visible_for(user=self.request.user)

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        ctx = super().get_context_data(**kwargs)
        q = self.request.GET.copy()
        q.pop("page", None)
        ctx["querystring"] = q.urlencode()
        return ctx


class ReviewDetailView(DetailView):
    model = Review
    template_name = "frontend/reviews/review_detail.html"
    context_object_name = "review"
    pk_url_kwarg = "pk"

    def get_object(self, queryset=None):  # noqa: ARG002
        obj = review_selectors.review_by_pk_for_user(pk=int(self.kwargs["pk"]), user=self.request.user)
        if obj is None:
            raise Http404()
        return obj


class ReviewCreateView(LoginRequiredMixin, FormView):
    form_class = ReviewCreateForm
    template_name = "frontend/reviews/review_create.html"
    login_url = _REVIEW_LOGIN_URL

    def dispatch(self, request, *args: object, **kwargs: object):
        self.medication = get_object_or_404(Medication, slug=kwargs["medication_slug"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        ctx = super().get_context_data(**kwargs)
        ctx["medication"] = self.medication
        return ctx

    def form_valid(self, form: ReviewCreateForm) -> HttpResponse:
        try:
            review = ReviewService.create_review(
                user=self.request.user,
                medication_id=self.medication.pk,
                rating=int(form.cleaned_data["rating"]),
                text=form.cleaned_data.get("text") or "",
            )
        except ValidationError as exc:
            for msg in exc.messages:
                form.add_error(None, msg)
            return self.form_invalid(form)
        messages.success(self.request, _("Отзыв отправлен на модерацию."))
        return HttpResponseRedirect(review.get_absolute_url())


class ReviewOwnerOrStaffMixin(UserPassesTestMixin):
    def test_func(self) -> bool:
        review = self.get_object()
        u = self.request.user
        return bool(u.is_staff or review.user_id == u.pk)


class ReviewUpdateView(LoginRequiredMixin, ReviewOwnerOrStaffMixin, UpdateView):
    model = Review
    form_class = ReviewUpdateForm
    template_name = "frontend/reviews/review_form.html"
    pk_url_kwarg = "pk"
    login_url = _REVIEW_LOGIN_URL

    def get_queryset(self):
        return Review.objects.select_related("user", "medication")

    def form_valid(self, form: ReviewUpdateForm) -> HttpResponse:
        try:
            ReviewService.update_review(
                review=self.object,
                user=self.request.user,
                rating=int(form.cleaned_data["rating"]),
                text=form.cleaned_data.get("text") or "",
            )
        except ValidationError as exc:
            for msg in exc.messages:
                form.add_error(None, msg)
            return self.form_invalid(form)
        messages.success(self.request, _("Сохранено."))
        return HttpResponseRedirect(self.object.get_absolute_url())


class ReviewDeleteView(LoginRequiredMixin, ReviewOwnerOrStaffMixin, DeleteView):
    model = Review
    template_name = "frontend/reviews/review_confirm_delete.html"
    success_url = reverse_lazy("reviews:review_list")
    login_url = _REVIEW_LOGIN_URL

    def get_queryset(self):
        return Review.objects.select_related("user", "medication")

    def form_valid(self, form):
        try:
            ReviewService.delete_review(review=self.object, user=self.request.user)
        except ValidationError as exc:
            for msg in exc.messages:
                messages.error(self.request, msg)
            return HttpResponseRedirect(self.object.get_absolute_url())
        messages.success(self.request, _("Отзыв удалён."))
        return HttpResponseRedirect(self.success_url)
