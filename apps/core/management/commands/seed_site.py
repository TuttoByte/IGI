"""
Идемпотентное наполнение контента публичного сайта (ЛР1):
баннеры, партнёры, «О компании» с историей, словарь терминов, вакансии, промокоды.

Запуск: python manage.py seed_site
Вызывается также из seed_demo, поэтому отдельно запускать не обязательно.
"""
from __future__ import annotations

import re
from datetime import date, timedelta
from decimal import Decimal
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont

from apps.core.models import (
    Banner,
    CompanyInfo,
    CompanyMilestone,
    EmploymentType,
    GlossaryTerm,
    Partner,
    PromoCode,
    Vacancy,
)
from apps.pharmacy.models import Department

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Медиафайлы, сгенерированные заранее и лежащие в репозитории (MEDIA_ROOT/company).
COMPANY_VIDEO = "company/promo.mp4"
COMPANY_POSTER = "company/promo-poster.jpg"
COMPANY_AUDIO = "company/jingle.mp3"


def _font(path: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Системный DejaVu, а если его нет — встроенный шрифт Pillow."""
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def _fitted_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    path: str,
    start_size: int,
    max_width: int,
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Подбирает кегль так, чтобы строка целиком помещалась в отведённую ширину."""
    size = start_size
    while size > 10:
        font = _font(path, size)
        if draw.textlength(text, font=font) <= max_width:
            return font
        size -= 2
    return _font(path, 10)


def _banner_bytes(
    title: str,
    subtitle: str,
    rgb: tuple[int, int, int],
    width: int,
    *,
    narrow: bool = False,
) -> bytes:
    """
    Рекламная картинка с текстом.

    narrow=True — вариант для узкого экрана: крупный текст в две строки под крестом
    (художественная адаптация через <picture><source media>, а не простое масштабирование).
    """
    height = round(width * 5 / 9) if narrow else round(width * 5 / 16)
    scale = width / (720 if narrow else 1440)
    img = Image.new("RGB", (width, height), rgb)
    draw = ImageDraw.Draw(img)
    for y in range(height):
        k = 1 - (y / height) * 0.4
        draw.line([(0, y), (width, y)], fill=tuple(min(255, int(c * k + 30)) for c in rgb))

    pad = int(40 * scale)
    if narrow:
        cx, cy, arm, thick = pad + int(44 * scale), int(84 * scale), int(40 * scale), int(26 * scale)
        text_x, title_y = pad, int(160 * scale)
        title_size, subtitle_size = int(58 * scale), int(32 * scale)
    else:
        cx, cy, arm, thick = int(120 * scale), height // 2, int(52 * scale), int(34 * scale)
        text_x, title_y = int(230 * scale), int(150 * scale)
        title_size, subtitle_size = int(74 * scale), int(38 * scale)

    draw.rectangle([cx - thick // 2, cy - arm, cx + thick // 2, cy + arm], fill=(255, 255, 255))
    draw.rectangle([cx - arm, cy - thick // 2, cx + arm, cy + thick // 2], fill=(255, 255, 255))

    available = width - text_x - pad
    title_font = _fitted_font(draw, title, FONT_BOLD, max(12, title_size), available)
    subtitle_font = _fitted_font(draw, subtitle, FONT_REGULAR, max(10, subtitle_size), available)
    draw.text((text_x, title_y), title, font=title_font, fill=(255, 255, 255))
    draw.text((text_x + 2, title_y + int(title_size * 1.35)), subtitle, font=subtitle_font, fill=(236, 242, 240))

    buf = BytesIO()
    img.save(buf, format="JPEG", quality=86, optimize=True)
    return buf.getvalue()


def _logo_bytes(name: str, rgb: tuple[int, int, int], size: tuple[int, int] = (320, 128)) -> bytes:
    """Логотип-заглушка: цветная плашка с названием компании по центру."""
    width, height = size
    img = Image.new("RGB", size, (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, width - 1, height - 1], outline=rgb, width=3)
    draw.rectangle([10, 10, 46, height - 11], fill=rgb)

    font = _font(FONT_BOLD, 26)
    words, lines, current = name.split(), [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) > width - 70 and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    lines = lines[:3]

    y = height // 2 - len(lines) * 16
    for line in lines:
        draw.text((60, y), line, font=font, fill=rgb)
        y += 32
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


def _certificate_bytes(company: str, number: str, issued: str, issuer: str) -> bytes:
    """Демо-скан сертификата: лист с рамкой, заголовком и реквизитами."""
    width, height = 900, 1270
    img = Image.new("RGB", (width, height), (252, 251, 246))
    draw = ImageDraw.Draw(img)
    accent, ink = (150, 32, 40), (30, 34, 48)

    # двойная декоративная рамка
    draw.rectangle([28, 28, width - 29, height - 29], outline=accent, width=6)
    draw.rectangle([46, 46, width - 47, height - 47], outline=accent, width=2)

    def centered(text: str, y: int, font, fill) -> None:
        draw.text(((width - draw.textlength(text, font=font)) / 2, y), text, font=font, fill=fill)

    centered("РЕСПУБЛИКА БЕЛАРУСЬ", 110, _font(FONT_REGULAR, 26), ink)
    centered("СВИДЕТЕЛЬСТВО", 175, _font(FONT_BOLD, 76), accent)
    centered("о соответствии системы менеджмента качества", 275, _font(FONT_REGULAR, 26), ink)
    draw.line([160, 330, width - 160, 330], fill=accent, width=2)

    # водяной знак — аптечный крест
    cx, cy, arm, thick = width // 2, 560, 150, 92
    faint = (238, 232, 228)
    draw.rectangle([cx - thick // 2, cy - arm, cx + thick // 2, cy + arm], fill=faint)
    draw.rectangle([cx - arm, cy - thick // 2, cx + arm, cy + thick // 2], fill=faint)

    centered("Настоящим удостоверяется, что", 420, _font(FONT_REGULAR, 24), ink)
    centered(company, 470, _font(FONT_BOLD, 32), ink)
    centered("применительно к розничной реализации", 545, _font(FONT_REGULAR, 24), ink)
    centered("лекарственных средств и изделий медицинского назначения", 580, _font(FONT_REGULAR, 24), ink)
    centered("соответствует требованиям СТБ ISO 9001-2015", 640, _font(FONT_BOLD, 28), accent)

    rows = [("Регистрационный номер:", number), ("Дата регистрации:", issued), ("Орган по сертификации:", issuer)]
    y = 760
    for label, value in rows:
        draw.text((150, y), label, font=_font(FONT_REGULAR, 22), fill=(110, 112, 122))
        # длинное название органа сжимаем, чтобы не выходило за рамку
        draw.text((150, y + 32), value, font=_fitted_font(draw, value, FONT_BOLD, 24, width - 300), fill=ink)
        y += 100

    draw.line([150, 1105, 430, 1105], fill=ink, width=1)
    draw.text((150, 1115), "Руководитель органа по сертификации", font=_font(FONT_REGULAR, 20), fill=(110, 112, 122))
    draw.ellipse([600, 1010, 790, 1200], outline=accent, width=4)
    centered_x = 695
    draw.text((centered_x - draw.textlength("М. П.", font=_font(FONT_BOLD, 30)) / 2, 1090),
              "М. П.", font=_font(FONT_BOLD, 30), fill=accent)

    buf = BytesIO()
    img.save(buf, format="JPEG", quality=88, optimize=True)
    return buf.getvalue()


def _safe(slug: str) -> str:
    return re.sub(r"[^a-z0-9_-]+", "-", slug.lower())[:80] or "image"


class Command(BaseCommand):
    help = "Наполняет публичный сайт: баннеры, партнёры, о компании, словарь, вакансии, промокоды."

    def handle(self, *args: object, **options: object) -> None:
        with transaction.atomic():
            self._seed_banners()
            self._seed_partners()
            self._seed_company()
            self._seed_glossary()
            self._seed_vacancies()
            self._seed_promocodes()
        self.stdout.write(self.style.SUCCESS("✓ Контент публичного сайта обновлён"))

    # ------------------------------------------------------------------ баннеры
    def _seed_banners(self) -> None:
        specs = [
            {
                "title": "Витамины −15%",
                "subtitle": "Весь сентябрь по промокоду VITAMIN15",
                "alt_text": "Рекламный баннер: скидка 15 процентов на витамины в сентябре",
                "link_url": "/promocodes/",
                "link_label": "Смотреть промокоды",
                "sort_order": 10,
                "rgb": (14, 111, 82),
            },
            {
                "title": "Заказ онлайн за 15 минут",
                "subtitle": "Соберём заказ и придержим до конца дня",
                "alt_text": "Рекламный баннер: онлайн-заказ лекарств с самовывозом за пятнадцать минут",
                "link_url": "/pharmacy/medications/",
                "link_label": "Открыть каталог",
                "sort_order": 20,
                "rgb": (24, 74, 124),
            },
            {
                "title": "Доставка бесплатно от 60 BYN",
                "subtitle": "Курьером по Минску в день заказа",
                "alt_text": "Рекламный баннер: бесплатная доставка заказов от шестидесяти рублей",
                "link_url": "/cart/",
                "link_label": "Перейти в корзину",
                "sort_order": 30,
                "rgb": (122, 62, 30),
            },
        ]
        for spec in specs:
            rgb = spec.pop("rgb")
            title = str(spec["title"])
            defaults = {k: v for k, v in spec.items() if k != "title"}
            banner, _created = Banner.objects.update_or_create(title=title, defaults=defaults)
            slug = _safe(f"banner-{banner.pk}")
            if not banner.image:
                banner.image.save(
                    f"{slug}-1440.jpg",
                    ContentFile(_banner_bytes(title, str(spec["subtitle"]), rgb, 1440)),
                    save=True,
                )
            if not banner.image_mobile:
                banner.image_mobile.save(
                    f"{slug}-720.jpg",
                    ContentFile(_banner_bytes(title, str(spec["subtitle"]), rgb, 720, narrow=True)),
                    save=True,
                )
        self.stdout.write(self.style.NOTICE(f"✓ Баннеры: {Banner.objects.count()}"))

    # ----------------------------------------------------------------- партнёры
    def _seed_partners(self) -> None:
        specs = [
            {
                "slug": "belmedpreparaty",
                "name": "Белмедпрепараты",
                "site_url": "https://belmedpreparaty.by/",
                "description": "Белорусский производитель лекарственных средств полного цикла.",
                "country": "Беларусь",
                "cooperation_since": 2010,
                "sort_order": 10,
                "rgb": (14, 111, 82),
            },
            {
                "slug": "borisovskiy-zavod",
                "name": "Борисовский завод медпрепаратов",
                "site_url": "https://borimed.com/",
                "description": "Таблетированные формы, растворы для инъекций, антибиотики.",
                "country": "Беларусь",
                "cooperation_since": 2012,
                "sort_order": 20,
                "rgb": (24, 74, 124),
            },
            {
                "slug": "krka",
                "name": "KRKA",
                "site_url": "https://www.krka.biz/",
                "description": "Дженерики европейского производства и товары для ухода.",
                "country": "Словения",
                "cooperation_since": 2015,
                "sort_order": 30,
                "rgb": (86, 44, 96),
            },
            {
                "slug": "gedeon-richter",
                "name": "Gedeon Richter",
                "site_url": "https://www.gedeonrichter.com/",
                "description": "Рецептурные препараты, женское здоровье, неврология.",
                "country": "Венгрия",
                "cooperation_since": 2018,
                "sort_order": 40,
                "rgb": (150, 78, 30),
            },
            {
                "slug": "medtekhnika-servis",
                "name": "Медтехника-Сервис",
                "site_url": "https://example.by/",
                "description": "Тонометры, глюкометры, изделия медицинского назначения.",
                "country": "Беларусь",
                "cooperation_since": 2021,
                "sort_order": 50,
                "rgb": (60, 96, 64),
            },
        ]
        for spec in specs:
            rgb = spec.pop("rgb")
            slug = str(spec["slug"])
            defaults = {k: v for k, v in spec.items() if k != "slug"}
            partner, _created = Partner.objects.update_or_create(slug=slug, defaults=defaults)
            if not partner.logo:
                partner.logo.save(
                    f"{_safe(slug)}.jpg",
                    ContentFile(_logo_bytes(str(spec["name"]), rgb)),
                    save=True,
                )
        self.stdout.write(self.style.NOTICE(f"✓ Партнёры: {Partner.objects.count()}"))

    # --------------------------------------------------------------- о компании
    def _seed_company(self) -> None:
        company, _created = CompanyInfo.objects.update_or_create(
            legal_name="Унитарное предприятие «Здоровье-Фарм»",
            defaults={
                "name": "Аптека «Здоровье»",
                "tagline": "Лекарства, которым доверяют с 2009 года",
                "founded_year": 2009,
                "about_text": (
                    "Аптечная сеть «Здоровье» объединяет девять аптек в Минске и области. "
                    "Мы работаем по лицензии Министерства здравоохранения Республики Беларусь "
                    "и отпускаем как безрецептурные, так и рецептурные препараты.\n\n"
                    "В каждой аптеке есть рецептурно-производственный отдел, холодильное "
                    "оборудование для термолабильных препаратов и провизор-консультант. "
                    "Онлайн-каталог показывает реальные остатки: товар резервируется сразу "
                    "после оформления заказа и хранится до конца рабочего дня."
                ),
                "mission": (
                    "Сделать доступ к качественным лекарствам простым и понятным: честные "
                    "остатки в каталоге, прозрачные цены и консультация специалиста без очереди."
                ),
                "quatrain": (
                    "Аптека светит поздним вечером,\n"
                    "когда в квартале гаснет свет,\n"
                    "и провизор за стойкой лечит нечем —\n"
                    "спокойным словом, что беды нет."
                ),
                "quatrain_author": "из корпоративного альманаха сети",
                "quote_text": (
                    "Лекарство становится лекарством только в правильной дозе; "
                    "всё остальное определяет обстоятельство."
                ),
                "quote_source": "Парацельс",
                "quote_source_url": "https://ru.wikipedia.org/wiki/Парацельс",
                "map_embed_url": (
                    "https://www.openstreetmap.org/export/embed.html"
                    "?bbox=27.5580%2C53.9060%2C27.5820%2C53.9180&layer=mapnik&marker=53.9120%2C27.5700"
                ),
                "address": "220005, г. Минск, пр-т Независимости, 58",
                "phone": "+375 (17) 300-11-22",
                "email": "info@pharmacy.local",
                "work_hours": "ежедневно 08:00–22:00, без обеда",
                "requisites": (
                    "Полное наименование: Унитарное предприятие «Здоровье-Фарм»\n"
                    "УНП: 191234567\n"
                    "ОКПО: 37281945\n"
                    "Юридический адрес: 220005, г. Минск, пр-т Независимости, 58\n"
                    "Расчётный счёт: BY24 AKBB 3012 0000 0012 3456 7890\n"
                    "Банк: ОАО «АСБ Беларусбанк», г. Минск\n"
                    "БИК: AKBBBY2X\n"
                    "Директор: Иванова Мария Сергеевна\n"
                    "Лицензия: № 02040/4567 от 12.03.2009, Минздрав Республики Беларусь"
                ),
                "certificate_title": "Сертификат соответствия системы менеджмента качества",
                "certificate_number": "BY/112 05.01.001 12345",
                "certificate_issued_at": date(2024, 2, 14),
                "certificate_issuer": "Национальный орган по оценке соответствия Республики Беларусь",
                "certificate_image_alt": (
                    "Скан свидетельства о соответствии системы менеджмента качества "
                    "СТБ ISO 9001-2015, выданного УП «Здоровье-Фарм»"
                ),
                "certificate_text": (
                    "СЕРТИФИКАТ СООТВЕТСТВИЯ\n"
                    "Регистрационный номер: BY/112 05.01.001 12345\n"
                    "Дата регистрации: 14 февраля 2024 г.\n"
                    "Действителен по: 13 февраля 2027 г.\n"
                    "\n"
                    "Настоящий сертификат удостоверяет, что система менеджмента качества\n"
                    "Унитарного предприятия «Здоровье-Фарм» (УНП 191234567),\n"
                    "220005, г. Минск, пр-т Независимости, 58,\n"
                    "применительно к розничной реализации лекарственных средств,\n"
                    "изделий медицинского назначения и медицинской техники\n"
                    "соответствует требованиям СТБ ISO 9001-2015.\n"
                    "\n"
                    "Орган по сертификации: Национальный орган по оценке соответствия\n"
                    "Республики Беларусь, аттестат аккредитации BY/112 003.01\n"
                    "\n"
                    "Руководитель органа по сертификации ______________ А. П. Осипенко\n"
                    "М. П."
                ),
                "is_active": True,
            },
        )

        if not company.certificate_image:
            company.certificate_image.save(
                "certificate.jpg",
                ContentFile(
                    _certificate_bytes(
                        company.legal_name,
                        company.certificate_number,
                        company.certificate_issued_at.strftime("%d.%m.%Y") if company.certificate_issued_at else "—",
                        company.certificate_issuer,
                    )
                ),
                save=True,
            )

        if not company.logo:
            company.logo.save(
                "company-logo.jpg",
                ContentFile(_logo_bytes("Аптека «Здоровье»", (14, 111, 82), size=(520, 260))),
                save=True,
            )

        # Видео, постер и аудио лежат в репозитории — присваиваем относительные пути.
        media_root = Path(settings.MEDIA_ROOT)
        for field_name, rel_path in (
            ("video", COMPANY_VIDEO),
            ("video_poster", COMPANY_POSTER),
            ("audio", COMPANY_AUDIO),
        ):
            if getattr(company, field_name):
                continue
            if (media_root / rel_path).exists():
                setattr(company, field_name, rel_path)
            else:
                self.stdout.write(self.style.WARNING(f"· Файл {rel_path} не найден — поле {field_name} пусто"))
        company.save(update_fields=["video", "video_poster", "audio"])

        milestones = [
            (2009, "Открыта первая аптека", "Пр-т Независимости, 58 — круглосуточный отдел.", 1, 6, "0.35"),
            (2012, "Рецептурно-производственный отдел", "Изготовление мазей и растворов по рецептам врачей.", 2, 14, "0.90"),
            (2015, "Сеть выросла до четырёх аптек", "Открыты точки в Уручье, Малиновке и Серебрянке.", 4, 31, "2.40"),
            (2018, "Собственный склад", "Температурные зоны +2…+8 °C и +15…+25 °C.", 6, 52, "4.75"),
            (2021, "Онлайн-каталог с остатками", "Резервирование товара и самовывоз за 15 минут.", 8, 74, "7.20"),
            (2024, "Сертификат СТБ ISO 9001-2015", "Подтверждена система менеджмента качества.", 9, 88, "9.60"),
        ]
        for year, title, description, pharmacies, employees, revenue in milestones:
            CompanyMilestone.objects.update_or_create(
                company=company,
                year=year,
                defaults={
                    "title": title,
                    "description": description,
                    "pharmacies_count": pharmacies,
                    "employees_count": employees,
                    "revenue_mln": Decimal(revenue),
                },
            )
        self.stdout.write(self.style.NOTICE(f"✓ О компании + история: {company.milestones.count()} записей"))

    # ------------------------------------------------------------------ словарь
    def _seed_glossary(self) -> None:
        today = timezone.localdate()
        specs = [
            {
                "slug": "mnn",
                "term": "Международное непатентованное наименование",
                "abbreviation": "МНН",
                "question": "Что такое МНН и зачем оно указано в карточке препарата?",
                "short_answer": "Уникальное название действующего вещества, единое во всём мире.",
                "answer": (
                    "МНН — это название действующего вещества, а не торговой марки. "
                    "Например, у торговых наименований «Панадол» и «Эффералган» одно МНН — парацетамол.\n"
                    "Зная МНН, фармацевт подберёт аналог, если нужного бренда нет в наличии, "
                    "а врач сможет проверить, не дублируются ли действующие вещества в назначениях."
                ),
                "added_at": today - timedelta(days=120),
                "sort_order": 10,
            },
            {
                "slug": "dzhenerik",
                "term": "Дженерик",
                "abbreviation": "",
                "question": "Чем дженерик отличается от оригинального препарата?",
                "short_answer": "Копия оригинала с тем же действующим веществом после истечения патента.",
                "answer": (
                    "Дженерик содержит то же действующее вещество в той же дозировке и лекарственной "
                    "форме, что и оригинал, и проходит проверку биоэквивалентности.\n"
                    "Отличаться могут вспомогательные вещества, оболочка таблетки и цена — обычно "
                    "дженерик дешевле, потому что производитель не оплачивает разработку молекулы."
                ),
                "added_at": today - timedelta(days=95),
                "sort_order": 20,
            },
            {
                "slug": "receptrunyy-otpusk",
                "term": "Рецептурный отпуск",
                "abbreviation": "Rx",
                "question": "Почему некоторые препараты нельзя купить без рецепта?",
                "short_answer": "Отпуск по рецепту защищает от неверной дозы и опасных сочетаний.",
                "answer": (
                    "Рецептурные препараты требуют контроля дозы, длительности курса и сочетаний "
                    "с другими лекарствами. К ним относятся антибиотики, гормональные средства, "
                    "сильные анальгетики.\n"
                    "Рецепт остаётся в аптеке или отмечается фармацевтом. В каталоге такие позиции "
                    "помечены значком «по рецепту» — заказать их онлайн можно, а получить только "
                    "при предъявлении рецепта."
                ),
                "added_at": today - timedelta(days=80),
                "sort_order": 30,
            },
            {
                "slug": "srok-godnosti",
                "term": "Срок годности",
                "abbreviation": "",
                "question": "Можно ли принимать препарат в последний день срока годности?",
                "short_answer": "Да, до конца указанного месяца включительно, если упаковка цела.",
                "answer": (
                    "Срок годности означает период, в течение которого производитель гарантирует "
                    "заявленное содержание действующего вещества при правильном хранении.\n"
                    "Если на упаковке указан только месяц и год, препарат годен до последнего дня "
                    "этого месяца. После вскрытия флакона или ампулы срок сокращается — он указан "
                    "в инструкции отдельно."
                ),
                "added_at": today - timedelta(days=60),
                "sort_order": 40,
            },
            {
                "slug": "usloviya-hraneniya",
                "term": "Условия хранения",
                "abbreviation": "",
                "question": "Что означает «хранить при температуре от +2 до +8 °C»?",
                "short_answer": "Холодильник, но не морозильник: заморозка портит препарат.",
                "answer": (
                    "Диапазон +2…+8 °C — это обычная полка холодильника, но не дверца и не "
                    "морозильная камера. Заморозка разрушает белковые препараты и вакцины "
                    "необратимо, даже если после оттаивания раствор выглядит прозрачным.\n"
                    "Для перевозки таких препаратов аптека выдаёт термопакет; довезти покупку "
                    "нужно в течение часа."
                ),
                "added_at": today - timedelta(days=45),
                "sort_order": 50,
            },
            {
                "slug": "pobochnoe-deystvie",
                "term": "Побочное действие",
                "abbreviation": "НЛР",
                "question": "Куда сообщить о нежелательной реакции на лекарство?",
                "short_answer": "Врачу, в аптеку и в национальную систему фармаконадзора.",
                "answer": (
                    "Нежелательная лекарственная реакция (НЛР) — любая непреднамеренная реакция "
                    "на препарат в обычной дозе.\n"
                    "Сообщите лечащему врачу и сохраните упаковку с номером серии. Аптека принимает "
                    "сообщение по телефону и передаёт его в систему фармаконадзора. Приём препарата "
                    "прекращают до консультации со специалистом."
                ),
                "added_at": today - timedelta(days=21),
                "sort_order": 60,
            },
            {
                "slug": "vozvrat-lekarstv",
                "term": "Возврат лекарственных средств",
                "abbreviation": "",
                "question": "Можно ли вернуть лекарство, если оно не подошло?",
                "short_answer": "Нет: препараты надлежащего качества обмену и возврату не подлежат.",
                "answer": (
                    "Лекарственные средства входят в перечень непродовольственных товаров "
                    "надлежащего качества, не подлежащих обмену и возврату.\n"
                    "Исключение — брак: повреждённая упаковка, несоответствие маркировки, "
                    "истёкший срок годности на момент продажи. В этом случае препарат "
                    "принимают обратно по чеку."
                ),
                "added_at": today - timedelta(days=10),
                "sort_order": 70,
            },
        ]
        for spec in specs:
            slug = str(spec["slug"])
            defaults = {k: v for k, v in spec.items() if k != "slug"}
            GlossaryTerm.objects.update_or_create(slug=slug, defaults=defaults)
        self.stdout.write(self.style.NOTICE(f"✓ Словарь терминов: {GlossaryTerm.objects.count()}"))

    # ----------------------------------------------------------------- вакансии
    def _seed_vacancies(self) -> None:
        today = timezone.localdate()
        departments = {d.name: d for d in Department.objects.all()}
        default_department = next(iter(departments.values()), None)

        specs = [
            {
                "slug": "provizor-receptrunogo-otdela",
                "title": "Провизор рецептурного отдела",
                "city": "Минск",
                "employment_type": EmploymentType.FULL_TIME,
                "description": (
                    "Отпуск рецептурных препаратов, консультирование покупателей и контроль "
                    "правильности оформления рецептов в аптеке на пр-те Независимости."
                ),
                "responsibilities": (
                    "Отпуск лекарственных средств по рецептам врачей\n"
                    "Проверка рецептов и ведение журнала предметно-количественного учёта\n"
                    "Консультирование по совместимости препаратов и подбор аналогов по МНН\n"
                    "Контроль сроков годности и температурного режима хранения"
                ),
                "requirements": (
                    "Высшее фармацевтическое образование\n"
                    "Действующий сертификат специалиста\n"
                    "Опыт работы от 2 лет в аптеке\n"
                    "Знание правил отпуска препаратов ПКУ"
                ),
                "salary_from": Decimal("1600.00"),
                "salary_to": Decimal("2100.00"),
                "experience_years": 2,
                "published_at": today - timedelta(days=3),
            },
            {
                "slug": "farmacevt-torgovogo-zala",
                "title": "Фармацевт торгового зала",
                "city": "Минск",
                "employment_type": EmploymentType.SHIFT,
                "description": (
                    "Работа в зале безрецептурного отпуска: помощь покупателям, выкладка товара, "
                    "работа с кассой. График 2/2 по 12 часов."
                ),
                "responsibilities": (
                    "Отпуск безрецептурных препаратов и товаров для ухода\n"
                    "Работа с кассовым аппаратом и оформление онлайн-заказов\n"
                    "Приёмка товара и выкладка по планограмме"
                ),
                "requirements": (
                    "Среднее специальное фармацевтическое образование\n"
                    "Готовность к сменному графику\n"
                    "Внимательность и доброжелательность"
                ),
                "salary_from": Decimal("1200.00"),
                "salary_to": Decimal("1500.00"),
                "experience_years": 0,
                "published_at": today - timedelta(days=8),
            },
            {
                "slug": "kladovshchik-sklada",
                "title": "Кладовщик аптечного склада",
                "city": "Минск",
                "employment_type": EmploymentType.FULL_TIME,
                "description": (
                    "Приёмка, размещение и комплектация лекарственных средств на складе "
                    "с температурными зонами."
                ),
                "responsibilities": (
                    "Приёмка товара по накладным и сверка серий\n"
                    "Размещение по температурным зонам +2…+8 °C и +15…+25 °C\n"
                    "Комплектация заказов для аптек сети\n"
                    "Участие в инвентаризациях"
                ),
                "requirements": (
                    "Опыт складской работы от 1 года\n"
                    "Уверенное владение программой складского учёта\n"
                    "Аккуратность в работе с документами"
                ),
                "salary_from": Decimal("1300.00"),
                "salary_to": Decimal("1650.00"),
                "experience_years": 1,
                "published_at": today - timedelta(days=14),
            },
            {
                "slug": "stazhirovka-studenta-farmfakulteta",
                "title": "Стажировка для студентов фармфакультета",
                "city": "Минск",
                "employment_type": EmploymentType.INTERNSHIP,
                "description": (
                    "Оплачиваемая стажировка на 3 месяца с наставником. Возможен гибкий график, "
                    "совместимый с учёбой, и трудоустройство по итогам."
                ),
                "responsibilities": (
                    "Работа с наставником в торговом зале\n"
                    "Знакомство с товароучётной системой аптеки\n"
                    "Помощь в приёмке и выкладке товара"
                ),
                "requirements": (
                    "Студент 3-5 курса фармацевтического факультета\n"
                    "Готовность работать от 20 часов в неделю\n"
                    "Интерес к работе с людьми"
                ),
                "salary_from": Decimal("700.00"),
                "salary_to": Decimal("950.00"),
                "experience_years": 0,
                "published_at": today - timedelta(days=20),
            },
        ]
        for spec in specs:
            slug = str(spec["slug"])
            defaults = {k: v for k, v in spec.items() if k != "slug"}
            defaults["department"] = default_department
            Vacancy.objects.update_or_create(slug=slug, defaults=defaults)
        self.stdout.write(self.style.NOTICE(f"✓ Вакансии: {Vacancy.objects.count()}"))

    # ---------------------------------------------------------------- промокоды
    def _seed_promocodes(self) -> None:
        today = timezone.localdate()
        specs = [
            {
                "code": "VITAMIN15",
                "title": "−15% на витамины и БАД",
                "description": "Действует на категорию «Витамины». Не суммируется с дисконтной картой.",
                "discount_percent": 15,
                "min_order_total": Decimal("30.00"),
                "usage_limit": 500,
                "used_count": 128,
                "valid_from": today - timedelta(days=10),
                "valid_to": today + timedelta(days=50),
                "is_active": True,
            },
            {
                "code": "FIRSTORDER",
                "title": "−10% на первый онлайн-заказ",
                "description": "Для новых покупателей, оформивших первый заказ через сайт.",
                "discount_percent": 10,
                "min_order_total": Decimal("20.00"),
                "usage_limit": 0,
                "used_count": 341,
                "valid_from": today - timedelta(days=200),
                "valid_to": today + timedelta(days=165),
                "is_active": True,
            },
            {
                "code": "CARE20",
                "title": "−20% на товары для ухода",
                "description": "Кремы, средства гигиены и косметика аптечных марок.",
                "discount_percent": 20,
                "min_order_total": Decimal("45.00"),
                "usage_limit": 200,
                "used_count": 57,
                "valid_from": today - timedelta(days=3),
                "valid_to": today + timedelta(days=25),
                "is_active": True,
            },
            {
                "code": "SENIOR12",
                "title": "−12% для покупателей 60+",
                "description": "Постоянная скидка при предъявлении пенсионного удостоверения.",
                "discount_percent": 12,
                "min_order_total": Decimal("0.00"),
                "usage_limit": 0,
                "used_count": 894,
                "valid_from": today - timedelta(days=400),
                "valid_to": today + timedelta(days=300),
                "is_active": True,
            },
            {
                "code": "SUMMER10",
                "title": "Летняя аптечка −10%",
                "description": "Солнцезащитные средства и препараты от укусов насекомых.",
                "discount_percent": 10,
                "min_order_total": Decimal("25.00"),
                "usage_limit": 300,
                "used_count": 300,
                "valid_from": today - timedelta(days=120),
                "valid_to": today - timedelta(days=30),
                "is_active": True,
            },
            {
                "code": "NEWYEAR25",
                "title": "Новогодняя акция −25%",
                "description": "Архивная акция прошлого сезона.",
                "discount_percent": 25,
                "min_order_total": Decimal("60.00"),
                "usage_limit": 400,
                "used_count": 388,
                "valid_from": today - timedelta(days=280),
                "valid_to": today - timedelta(days=250),
                "is_active": False,
            },
            {
                "code": "AUTUMN18",
                "title": "Осенний иммунитет −18%",
                "description": "Стартует в следующем месяце — пока недоступен к применению.",
                "discount_percent": 18,
                "min_order_total": Decimal("35.00"),
                "usage_limit": 250,
                "used_count": 0,
                "valid_from": today + timedelta(days=20),
                "valid_to": today + timedelta(days=80),
                "is_active": True,
            },
        ]
        for spec in specs:
            code = str(spec["code"])
            defaults = {k: v for k, v in spec.items() if k != "code"}
            PromoCode.objects.update_or_create(code=code, defaults=defaults)
        self.stdout.write(self.style.NOTICE(f"✓ Промокоды: {PromoCode.objects.count()}"))
