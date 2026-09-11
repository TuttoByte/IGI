"""Публичный контент сайта: новости, контакты, компания, вакансии, промокоды."""
from __future__ import annotations

from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.pharmacy.slug import SlugService


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(_("создано"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("обновлено"), auto_now=True)

    class Meta:
        abstract = True


class NewsArticle(TimeStampedModel):
    """Новость аптеки: публикация всегда с изображением."""

    title = models.CharField(_("заголовок"), max_length=255)
    slug = models.SlugField(_("слаг"), max_length=255, unique=True)
    image = models.ImageField(_("изображение"), upload_to="news/%Y/%m/")
    lead = models.TextField(_("анонс"))
    content = models.TextField(_("текст новости"))
    published_at = models.DateTimeField(_("дата публикации"), default=timezone.now, db_index=True)
    is_published = models.BooleanField(_("опубликовано"), default=True, db_index=True)

    class Meta:
        verbose_name = _("новость")
        verbose_name_plural = _("новости")
        ordering = ("-published_at", "-created_at")
        indexes = [
            models.Index(fields=["is_published", "-published_at"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["title"]),
        ]

    def __str__(self) -> str:
        return self.title

    def save(self, *args: object, **kwargs: object) -> None:
        SlugService.assign_if_blank(self, source_field="title", max_length=80)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("core:news_detail", kwargs={"slug": self.slug})


class EmployeeContact(TimeStampedModel):
    """Карточка сотрудника для страницы контактов."""

    full_name = models.CharField(_("ФИО"), max_length=255)
    slug = models.SlugField(_("слаг"), max_length=255, unique=True)
    position = models.CharField(_("должность"), max_length=255)
    photo = models.ImageField(_("фотография"), upload_to="employees/%Y/%m/")
    phone = models.CharField(_("телефон"), max_length=40, blank=True)
    email = models.EmailField(_("email"), blank=True)
    work_calendar = models.TextField(_("текстовый календарь"))
    note = models.TextField(_("информация"), blank=True)
    sort_order = models.PositiveSmallIntegerField(_("порядок"), default=100, db_index=True)
    is_active = models.BooleanField(_("показывать на сайте"), default=True, db_index=True)

    class Meta:
        verbose_name = _("контакт сотрудника")
        verbose_name_plural = _("контакты сотрудников")
        ordering = ("sort_order", "full_name")
        indexes = [
            models.Index(fields=["is_active", "sort_order", "full_name"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self) -> str:
        return self.full_name

    def save(self, *args: object, **kwargs: object) -> None:
        SlugService.assign_if_blank(self, source_field="full_name", max_length=80)
        super().save(*args, **kwargs)


class Banner(TimeStampedModel):
    """Рекламный баннер главной страницы: две ширины изображения для srcset."""

    title = models.CharField(_("заголовок"), max_length=255)
    subtitle = models.CharField(_("подзаголовок"), max_length=255, blank=True)
    image = models.ImageField(_("изображение 1440px"), upload_to="banners/%Y/%m/")
    image_mobile = models.ImageField(
        _("изображение 720px"),
        upload_to="banners/%Y/%m/",
        blank=True,
        help_text=_("Узкий вариант для srcset; если пусто — используется основное."),
    )
    alt_text = models.CharField(_("альтернативный текст"), max_length=255)
    link_url = models.CharField(_("ссылка"), max_length=500, blank=True)
    link_label = models.CharField(_("текст ссылки"), max_length=120, blank=True)
    sort_order = models.PositiveSmallIntegerField(_("порядок"), default=100, db_index=True)
    is_active = models.BooleanField(_("показывать"), default=True, db_index=True)

    class Meta:
        verbose_name = _("рекламный баннер")
        verbose_name_plural = _("рекламные баннеры")
        ordering = ("sort_order", "-created_at")
        indexes = [models.Index(fields=["is_active", "sort_order"])]

    def __str__(self) -> str:
        return self.title


class Partner(TimeStampedModel):
    """Компания-партнёр: логотип и внешняя ссылка на сайт."""

    name = models.CharField(_("название"), max_length=255)
    slug = models.SlugField(_("слаг"), max_length=255, unique=True)
    logo = models.ImageField(_("логотип"), upload_to="partners/%Y/%m/")
    site_url = models.URLField(_("сайт"), max_length=500)
    description = models.CharField(_("краткое описание"), max_length=255, blank=True)
    country = models.CharField(_("страна"), max_length=120, blank=True)
    cooperation_since = models.PositiveSmallIntegerField(
        _("сотрудничаем с"),
        validators=[MinValueValidator(1990), MaxValueValidator(2100)],
        null=True,
        blank=True,
    )
    sort_order = models.PositiveSmallIntegerField(_("порядок"), default=100, db_index=True)
    is_active = models.BooleanField(_("показывать"), default=True, db_index=True)

    class Meta:
        verbose_name = _("партнёр")
        verbose_name_plural = _("партнёры")
        ordering = ("sort_order", "name")
        indexes = [
            models.Index(fields=["is_active", "sort_order", "name"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self) -> str:
        return self.name

    def save(self, *args: object, **kwargs: object) -> None:
        SlugService.assign_if_blank(self, source_field="name", max_length=80)
        super().save(*args, **kwargs)


class CompanyInfo(TimeStampedModel):
    """
    Страница «О компании» одной записью.

    Синглтон: страница читает первую активную запись (см. selectors.company_info).
    """

    name = models.CharField(_("название"), max_length=255)
    legal_name = models.CharField(_("юридическое наименование"), max_length=255)
    tagline = models.CharField(_("слоган"), max_length=255, blank=True)
    logo = models.ImageField(_("логотип"), upload_to="company/", blank=True)
    video = models.FileField(
        _("видеоролик"),
        upload_to="company/",
        blank=True,
        help_text=_("MP4 (H.264) — воспроизводится тегом <video> на странице о компании."),
    )
    video_poster = models.ImageField(_("постер видео"), upload_to="company/", blank=True)
    audio = models.FileField(
        _("аудиоролик"),
        upload_to="company/",
        blank=True,
        help_text=_("MP3 — воспроизводится тегом <audio>."),
    )
    founded_year = models.PositiveSmallIntegerField(
        _("год основания"),
        validators=[MinValueValidator(1900), MaxValueValidator(2100)],
        default=2009,
    )
    about_text = models.TextField(_("информация о компании"))
    mission = models.TextField(_("миссия"), blank=True)
    quatrain = models.TextField(
        _("четверостишие"),
        blank=True,
        help_text=_("Выводится в <pre> с сохранением авторских переводов строк."),
    )
    quatrain_author = models.CharField(_("автор четверостишия"), max_length=255, blank=True)
    quote_text = models.TextField(_("цитата"), blank=True)
    quote_source = models.CharField(_("источник цитаты"), max_length=255, blank=True)
    quote_source_url = models.URLField(_("ссылка на источник"), max_length=500, blank=True)
    map_embed_url = models.URLField(
        _("карта (iframe)"),
        max_length=1000,
        blank=True,
        help_text=_("URL для встраивания карты в <iframe>."),
    )
    address = models.CharField(_("адрес"), max_length=255, blank=True)
    phone = models.CharField(_("телефон"), max_length=40, blank=True)
    email = models.EmailField(_("email"), blank=True)
    work_hours = models.CharField(_("часы работы"), max_length=255, blank=True)
    requisites = models.TextField(
        _("реквизиты"),
        blank=True,
        help_text=_("Строки вида «Ключ: значение» — выводятся списком определений."),
    )
    certificate_title = models.CharField(_("название сертификата"), max_length=255, blank=True)
    certificate_number = models.CharField(_("номер сертификата"), max_length=120, blank=True)
    certificate_issued_at = models.DateField(_("дата выдачи сертификата"), null=True, blank=True)
    certificate_issuer = models.CharField(_("кем выдан"), max_length=255, blank=True)
    certificate_image = models.ImageField(
        _("фото сертификата"),
        upload_to="company/",
        blank=True,
        help_text=_("Скан или фотография. Если загружено — показывается вместо текста."),
    )
    certificate_image_alt = models.CharField(
        _("описание фото сертификата"),
        max_length=255,
        blank=True,
        help_text=_("Что изображено — читается скринридером вместо картинки."),
    )
    certificate_text = models.TextField(
        _("текст сертификата"),
        blank=True,
        help_text=_("Показывается, если фото не загружено; иначе доступен как расшифровка."),
    )
    is_active = models.BooleanField(_("активная запись"), default=True, db_index=True)

    class Meta:
        verbose_name = _("информация о компании")
        verbose_name_plural = _("информация о компании")
        ordering = ("-is_active", "-updated_at")

    def __str__(self) -> str:
        return self.name

    def requisites_pairs(self) -> list[tuple[str, str]]:
        """Разбирает строки «Ключ: значение» для вывода в <dl>."""
        pairs: list[tuple[str, str]] = []
        for line in self.requisites.splitlines():
            if ":" not in line:
                continue
            key, _sep, value = line.partition(":")
            key, value = key.strip(), value.strip()
            if key and value:
                pairs.append((key, value))
        return pairs


class CompanyMilestone(models.Model):
    """Строка истории компании по годам."""

    company = models.ForeignKey(
        CompanyInfo,
        verbose_name=_("компания"),
        on_delete=models.CASCADE,
        related_name="milestones",
    )
    year = models.PositiveSmallIntegerField(
        _("год"),
        validators=[MinValueValidator(1900), MaxValueValidator(2100)],
        db_index=True,
    )
    title = models.CharField(_("событие"), max_length=255)
    description = models.TextField(_("описание"), blank=True)
    pharmacies_count = models.PositiveSmallIntegerField(_("аптек в сети"), default=1)
    employees_count = models.PositiveSmallIntegerField(_("сотрудников"), default=1)
    revenue_mln = models.DecimalField(
        _("выручка, млн BYN"),
        max_digits=8,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )

    class Meta:
        verbose_name = _("веха истории")
        verbose_name_plural = _("история по годам")
        ordering = ("year",)
        constraints = [
            models.UniqueConstraint(fields=("company", "year"), name="core_unique_company_year"),
        ]

    def __str__(self) -> str:
        return f"{self.year} — {self.title}"


class GlossaryTerm(TimeStampedModel):
    """Термин словаря / часто задаваемый вопрос с датой добавления на сайт."""

    term = models.CharField(_("термин"), max_length=255)
    slug = models.SlugField(_("слаг"), max_length=255, unique=True)
    abbreviation = models.CharField(
        _("сокращение"),
        max_length=40,
        blank=True,
        help_text=_("Выводится тегом <abbr> рядом с термином."),
    )
    question = models.CharField(_("вопрос"), max_length=255)
    short_answer = models.CharField(_("краткий ответ"), max_length=255, blank=True)
    answer = models.TextField(_("развёрнутый ответ"))
    added_at = models.DateField(_("дата добавления"), default=timezone.localdate, db_index=True)
    sort_order = models.PositiveSmallIntegerField(_("порядок"), default=100, db_index=True)
    is_published = models.BooleanField(_("опубликовано"), default=True, db_index=True)

    class Meta:
        verbose_name = _("термин словаря")
        verbose_name_plural = _("словарь терминов и понятий")
        ordering = ("sort_order", "term")
        indexes = [
            models.Index(fields=["is_published", "sort_order", "term"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["added_at"]),
        ]

    def __str__(self) -> str:
        return self.term

    def save(self, *args: object, **kwargs: object) -> None:
        SlugService.assign_if_blank(self, source_field="term", max_length=80)
        super().save(*args, **kwargs)


class EmploymentType(models.TextChoices):
    FULL_TIME = "FULL_TIME", _("Полная занятость")
    PART_TIME = "PART_TIME", _("Частичная занятость")
    SHIFT = "SHIFT", _("Сменный график")
    INTERNSHIP = "INTERNSHIP", _("Стажировка")


class Vacancy(TimeStampedModel):
    """Открытая вакансия аптечной сети."""

    title = models.CharField(_("должность"), max_length=255)
    slug = models.SlugField(_("слаг"), max_length=255, unique=True)
    department = models.ForeignKey(
        "pharmacy.Department",
        verbose_name=_("отдел"),
        on_delete=models.SET_NULL,
        related_name="vacancies",
        null=True,
        blank=True,
    )
    city = models.CharField(_("город"), max_length=120, default="Минск")
    employment_type = models.CharField(
        _("тип занятости"),
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
        db_index=True,
    )
    description = models.TextField(_("описание"))
    responsibilities = models.TextField(
        _("обязанности"),
        blank=True,
        help_text=_("По одному пункту на строку — выводится маркированным списком."),
    )
    requirements = models.TextField(
        _("требования"),
        blank=True,
        help_text=_("По одному пункту на строку — выводится нумерованным списком."),
    )
    salary_from = models.DecimalField(
        _("зарплата от, BYN"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    salary_to = models.DecimalField(
        _("зарплата до, BYN"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    experience_years = models.PositiveSmallIntegerField(_("опыт, лет"), default=0)
    published_at = models.DateField(_("опубликована"), default=timezone.localdate, db_index=True)
    is_open = models.BooleanField(_("открыта"), default=True, db_index=True)

    class Meta:
        verbose_name = _("вакансия")
        verbose_name_plural = _("вакансии")
        ordering = ("-published_at", "title")
        indexes = [
            models.Index(fields=["is_open", "-published_at"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["employment_type"]),
        ]

    def __str__(self) -> str:
        return self.title

    def save(self, *args: object, **kwargs: object) -> None:
        SlugService.assign_if_blank(self, source_field="title", max_length=80)
        super().save(*args, **kwargs)

    def responsibility_lines(self) -> list[str]:
        return [line.strip() for line in self.responsibilities.splitlines() if line.strip()]

    def requirement_lines(self) -> list[str]:
        return [line.strip() for line in self.requirements.splitlines() if line.strip()]


class PromoCode(TimeStampedModel):
    """Промокод/купон: действующий определяется окном дат и флагом is_active."""

    code = models.CharField(_("код"), max_length=32, unique=True, db_index=True)
    title = models.CharField(_("название акции"), max_length=255)
    description = models.TextField(_("условия"), blank=True)
    discount_percent = models.PositiveSmallIntegerField(
        _("скидка, %"),
        validators=[MinValueValidator(1), MaxValueValidator(90)],
    )
    min_order_total = models.DecimalField(
        _("минимальная сумма заказа, BYN"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    usage_limit = models.PositiveIntegerField(_("лимит применений"), default=0)
    used_count = models.PositiveIntegerField(_("использовано"), default=0)
    valid_from = models.DateField(_("действует с"), default=timezone.localdate, db_index=True)
    valid_to = models.DateField(_("действует по"), db_index=True)
    is_active = models.BooleanField(_("включён"), default=True, db_index=True)

    class Meta:
        verbose_name = _("промокод")
        verbose_name_plural = _("промокоды и купоны")
        ordering = ("-valid_to", "code")
        indexes = [
            models.Index(fields=["is_active", "valid_from", "valid_to"]),
            models.Index(fields=["code"]),
        ]

    def __str__(self) -> str:
        return self.code

    def is_current(self) -> bool:
        """Действует ли промокод на сегодняшнюю дату."""
        today = timezone.localdate()
        return bool(self.is_active and self.valid_from <= today <= self.valid_to)

    def remaining_uses(self) -> int:
        """Сколько применений осталось; при usage_limit == 0 лимита нет."""
        if not self.usage_limit:
            return 0
        return max(self.usage_limit - self.used_count, 0)
