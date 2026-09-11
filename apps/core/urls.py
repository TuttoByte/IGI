from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("news/", views.NewsListView.as_view(), name="news_list"),
    path("news/<slug:slug>/", views.NewsDetailView.as_view(), name="news_detail"),
    path("glossary/", views.GlossaryView.as_view(), name="glossary"),
    path("contacts/", views.ContactsView.as_view(), name="contacts"),
    path("privacy/", views.PrivacyPolicyView.as_view(), name="privacy"),
    path("vacancies/", views.VacancyListView.as_view(), name="vacancies"),
    path("promocodes/", views.PromoCodeListView.as_view(), name="promocodes"),
]
