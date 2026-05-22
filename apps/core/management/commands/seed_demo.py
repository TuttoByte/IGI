"""
Идемпотентное наполнение: демо-пользователи, расширенный каталог с фото, поставщики.

Запуск: python manage.py seed_demo
"""
from __future__ import annotations

import hashlib
import re
from datetime import date, timedelta
from decimal import Decimal
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from PIL import Image

from apps.accounts.models import Profile, UserRole
from apps.core.models import EmployeeContact, NewsArticle
from apps.pharmacy.models import Category, Department, Medication
from apps.suppliers.models import Supplier

DEMO_PASSWORD = "PharmaDemo2026!"


def _placeholder_jpeg_bytes(rgb: tuple[int, int, int]) -> bytes:
    img = Image.new("RGB", (480, 360), rgb)
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=88)
    return buf.getvalue()


def _stable_color(text: str) -> tuple[int, int, int]:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return (
        70 + digest[0] % 130,
        70 + digest[1] % 130,
        70 + digest[2] % 130,
    )


class Command(BaseCommand):
    help = "Создаёт demo_admin, demo_client, демо-каталог с изображениями и поставщиков (идемпотентно)."

    def handle(self, *args: object, **options: object) -> None:
        with transaction.atomic():
            self._seed_users()
            self._seed_catalog()
            self._seed_suppliers()
            self._seed_public_content()
        self.stdout.write(
            self.style.SUCCESS(
                "\n╔════════════════════════════════════════════╗\n"
                "║  Демо-доступ (логин / пароль)              ║\n"
                "╠════════════════════════════════════════════╣\n"
                f"║  demo_admin   /  {DEMO_PASSWORD:<22} ║\n"
                f"║  demo_client  /  {DEMO_PASSWORD:<22} ║\n"
                "╚════════════════════════════════════════════╝\n"
            )
        )

    def _seed_users(self) -> None:
        User = get_user_model()
        if not User.objects.filter(username="demo_admin").exists():
            User.objects.create_superuser(
                username="demo_admin",
                email="admin@demo.local",
                password=DEMO_PASSWORD,
            )
            self.stdout.write(self.style.NOTICE("✓ Создан пользователь demo_admin (ADMIN, staff)"))
        else:
            self.stdout.write("· demo_admin уже есть — пропуск")

        if not User.objects.filter(username="demo_client").exists():
            user = User.objects.create_user(
                username="demo_client",
                email="client@demo.local",
                password=DEMO_PASSWORD,
                role=UserRole.CUSTOMER,
            )
            Profile.objects.create(
                user=user,
                birth_date=date(1995, 6, 15),
                phone="+375 (29) 111-22-33",
                address="г. Минск, ул. Демо, 1",
            )
            self.stdout.write(self.style.NOTICE("✓ Создан пользователь demo_client (CUSTOMER)"))
        else:
            self.stdout.write("· demo_client уже есть — пропуск")

    def _demo_med_specs(self, today: date) -> list[dict[str, object]]:
        cat_obez, _ = Category.objects.get_or_create(
            slug="obezbolivayushie",
            defaults={"name": "Обезболивающие", "description": "НПВС и анальгетики."},
        )
        cat_vit, _ = Category.objects.get_or_create(
            slug="vitaminy",
            defaults={"name": "Витамины и БАД", "description": "Поддержка иммунитета."},
        )
        cat_gastro, _ = Category.objects.get_or_create(
            slug="gastro",
            defaults={"name": "ЖКТ", "description": "Препараты для желудочно-кишечного тракта."},
        )
        cat_aller, _ = Category.objects.get_or_create(
            slug="allergiya",
            defaults={"name": "Аллергия", "description": "Антигистаминные средства."},
        )
        cat_meta, _ = Category.objects.get_or_create(
            slug="endokrinologiya",
            defaults={"name": "Эндокринология", "description": "Сахарный диабет и обмен веществ."},
        )
        cat_antib, _ = Category.objects.get_or_create(
            slug="antibiotiki",
            defaults={"name": "Антибиотики", "description": "Бактериальные инфекции (по рецепту)."},
        )
        dep_zal1, _ = Department.objects.get_or_create(
            slug="zal-1",
            defaults={"name": "Зал №1 (открытый доступ)", "floor": 1, "description": "Основная торговая зона."},
        )
        dep_zal2, _ = Department.objects.get_or_create(
            slug="zal-2",
            defaults={"name": "Зал №2 (рецептурный)", "floor": 2, "description": "Рецептурные препараты."},
        )
        return [
            {
                "code": "ASP-500-DEMO",
                "name": "Аспирин таблетки 500 мг",
                "slug": "aspirin-500-demo",
                "description": "Нестероидный противовоспалительный препарат.",
                "instruction": "Принимать после еды по назначению врача.",
                "manufacturer": "ОАО «ДемоФарм»",
                "price": Decimal("4.20"),
                "quantity": 120,
                "expiration_date": today + timedelta(days=400),
                "requires_prescription": False,
                "category": cat_obez,
                "department": dep_zal1,
                "image_color": (200, 72, 65),
            },
            {
                "code": "PAR-250-DEMO",
                "name": "Парацетамол 250 мг",
                "slug": "paracetamol-250-demo",
                "description": "Жаропонижающее и обезболивающее.",
                "instruction": "Не превышать суточную дозу.",
                "manufacturer": "ОАО «ДемоФарм»",
                "price": Decimal("2.50"),
                "quantity": 8,
                "expiration_date": today + timedelta(days=200),
                "requires_prescription": False,
                "category": cat_obez,
                "department": dep_zal1,
                "image_color": (72, 118, 210),
            },
            {
                "code": "RX-AMOX-DEMO",
                "name": "Амоксициллин (рецепт)",
                "slug": "amoxicillin-demo",
                "description": "Антибиотик широкого спектра (демо-запись).",
                "instruction": "Только по рецепту врача. Курс до конца.",
                "manufacturer": "Импорт Демо Лтд",
                "price": Decimal("18.90"),
                "quantity": 25,
                "expiration_date": today + timedelta(days=180),
                "requires_prescription": True,
                "category": cat_antib,
                "department": dep_zal2,
                "image_color": (78, 168, 102),
            },
            {
                "code": "IBU-200-DEMO",
                "name": "Ибупрофен 200 мг",
                "slug": "ibuprofen-200-demo",
                "description": "НПВС, обезболивание и воспаление.",
                "instruction": "После еды, не на голодный желудок.",
                "manufacturer": "ОАО «ДемоФарм»",
                "price": Decimal("5.40"),
                "quantity": 95,
                "expiration_date": today + timedelta(days=300),
                "requires_prescription": False,
                "category": cat_obez,
                "department": dep_zal1,
                "image_color": (190, 140, 55),
            },
            {
                "code": "VIT-C-DEMO",
                "name": "Витамин C 500 мг",
                "slug": "vitamin-c-500-demo",
                "description": "Аскорбиновая кислота, поддержка иммунитета.",
                "instruction": "По 1 таблетке в день или по рекомендации.",
                "manufacturer": "БАД Демо ООО",
                "price": Decimal("6.10"),
                "quantity": 200,
                "expiration_date": today + timedelta(days=500),
                "requires_prescription": False,
                "category": cat_vit,
                "department": dep_zal1,
                "image_color": (230, 120, 50),
            },
            {
                "code": "OME-20-DEMO",
                "name": "Омепразол 20 мг",
                "slug": "omeprazole-20-demo",
                "description": "Ингибитор протонного насоса.",
                "instruction": "Утром натощак, курс по назначению врача.",
                "manufacturer": "МедДемо Плюс",
                "price": Decimal("7.80"),
                "quantity": 60,
                "expiration_date": today + timedelta(days=240),
                "requires_prescription": False,
                "category": cat_gastro,
                "department": dep_zal1,
                "image_color": (120, 90, 170),
            },
            {
                "code": "LOR-10-DEMO",
                "name": "Лоратадин 10 мг",
                "slug": "loratadine-10-demo",
                "description": "Антигистаминное средство длительного действия.",
                "instruction": "1 раз в сутки, независимо от еды.",
                "manufacturer": "АллергоДемо",
                "price": Decimal("3.90"),
                "quantity": 140,
                "expiration_date": today + timedelta(days=320),
                "requires_prescription": False,
                "category": cat_aller,
                "department": dep_zal1,
                "image_color": (60, 160, 190),
            },
            {
                "code": "MET-500-DEMO",
                "name": "Метформин 500 мг (рецепт)",
                "slug": "metformin-500-demo",
                "description": "Пероральный гипогликемический препарат.",
                "instruction": "Только по рецепту. Контроль функции почек.",
                "manufacturer": "ДиабетДемо АО",
                "price": Decimal("4.50"),
                "quantity": 40,
                "expiration_date": today + timedelta(days=150),
                "requires_prescription": True,
                "category": cat_meta,
                "department": dep_zal2,
                "image_color": (110, 110, 120),
            },
        ]

    def _attach_image_if_missing(self, med: Medication, rgb: tuple[int, int, int]) -> None:
        if med.image:
            return
        data = _placeholder_jpeg_bytes(rgb)
        safe = re.sub(r"[^a-z0-9_-]+", "-", med.slug.lower())[:80] or "med"
        med.image.save(f"{safe}.jpg", ContentFile(data), save=True)

    def _attach_required_image_if_missing(
        self,
        obj: object,
        *,
        field_name: str,
        slug: str,
        rgb: tuple[int, int, int],
    ) -> None:
        field = getattr(obj, field_name)
        if field:
            return
        data = _placeholder_jpeg_bytes(rgb)
        safe = re.sub(r"[^a-z0-9_-]+", "-", slug.lower())[:80] or "image"
        field.save(f"{safe}.jpg", ContentFile(data), save=True)

    def _seed_catalog(self) -> None:
        today = date.today()
        specs = self._demo_med_specs(today)
        created = 0
        updated = 0
        for row in specs:
            color = row.pop("image_color")
            assert isinstance(color, tuple)
            code = str(row["code"])
            defaults = {k: v for k, v in row.items() if k != "code"}
            med, was_created = Medication.objects.update_or_create(code=code, defaults=defaults)
            if was_created:
                created += 1
            else:
                updated += 1
            self._attach_image_if_missing(med, color)
        filled_missing = 0
        for med in Medication.objects.filter(image="").order_by("code", "name"):
            self._attach_image_if_missing(med, _stable_color(med.slug or med.name))
            filled_missing += 1
        self.stdout.write(
            self.style.NOTICE(
                "✓ Каталог: "
                f"создано {created}, обновлено по коду {updated}; "
                f"изображения без фото — добавлены ({filled_missing} старых записей)."
            )
        )

    def _seed_suppliers(self) -> None:
        s1, c1 = Supplier.objects.get_or_create(
            contract_number="DEMO-SUP-001",
            defaults={
                "name": "ООО «ДемоПоставка»",
                "slug": "ooo-demo-postavka",
                "email": "zakaz@demosupplier.local",
                "phone": "+375 (29) 999-88-77",
                "address": "РБ, г. Минск, пр-т Поставщиков, 10",
            },
        )
        s2, c2 = Supplier.objects.get_or_create(
            contract_number="DEMO-SUP-002",
            defaults={
                "name": "ИП ДемоИмпорт",
                "slug": "ip-demo-import",
                "email": "sales@demoimport.local",
                "phone": "+375 (29) 888-77-66",
                "address": "РБ, г. Гродно, ул. Складская, 3",
            },
        )
        if c1 or c2:
            self.stdout.write(self.style.NOTICE("✓ Созданы демо-поставщики"))

        demo_meds = list(Medication.objects.filter(code__endswith="-DEMO").order_by("code"))
        if not demo_meds:
            self.stdout.write("· Нет демо-препаратов (код *-DEMO) — связи пропущены")
            return
        s1.medications.clear()
        s2.medications.clear()
        for i, m in enumerate(demo_meds):
            (s1 if i % 2 == 0 else s2).medications.add(m)
        self.stdout.write(self.style.NOTICE("✓ Связи поставщик ↔ демо-препараты обновлены"))

    def _seed_public_content(self) -> None:
        now = timezone.now()
        news_specs = [
            {
                "title": "Новый раздел с аптечными новостями",
                "slug": "novyy-razdel-s-aptechnymi-novostyami",
                "lead": "Публикуем обновления ассортимента, полезные напоминания и важные объявления.",
                "content": (
                    "В новостях аптеки будут появляться материалы о поступлениях, сезонных товарах "
                    "и изменениях в работе отделов.\n\nВсе публикации сопровождаются изображениями, "
                    "чтобы лента оставалась наглядной для покупателей."
                ),
                "published_at": now - timedelta(days=1),
                "image_color": (42, 125, 96),
            },
            {
                "title": "Сезонная проверка домашней аптечки",
                "slug": "sezonnaya-proverka-domashney-aptechki",
                "lead": "Проверьте сроки годности базовых средств и пополните запасы заранее.",
                "content": (
                    "Перед сменой сезона полезно пересмотреть домашнюю аптечку: убрать просроченные "
                    "препараты, проверить жаропонижающие, перевязочные материалы и средства для ЖКТ.\n\n"
                    "Если лекарство требует рецепта, уточните наличие и правила отпуска у сотрудника аптеки."
                ),
                "published_at": now - timedelta(days=4),
                "image_color": (58, 96, 170),
            },
            {
                "title": "Как читать карточку препарата в каталоге",
                "slug": "kak-chitat-kartochku-preparata-v-kataloge",
                "lead": "В карточке видны остатки, отдел, срок годности, поставщики и отзывы покупателей.",
                "content": (
                    "Каталог помогает быстро найти препарат по названию, коду, производителю или категории. "
                    "На странице препарата отображаются цена, остаток, отдел и отметка о рецептурном отпуске.\n\n"
                    "Отзывы проходят модерацию, поэтому публично показываются только опубликованные записи."
                ),
                "published_at": now - timedelta(days=7),
                "image_color": (180, 94, 55),
            },
        ]

        for spec in news_specs:
            color = spec.pop("image_color")
            assert isinstance(color, tuple)
            slug = str(spec["slug"])
            defaults = {key: value for key, value in spec.items() if key != "slug"}
            article, _created = NewsArticle.objects.update_or_create(slug=slug, defaults=defaults)
            self._attach_required_image_if_missing(
                article,
                field_name="image",
                slug=slug,
                rgb=color,
            )

        employee_specs = [
            {
                "full_name": "Иванова Мария Сергеевна",
                "slug": "ivanova-mariya-sergeevna",
                "position": "Заведующая аптекой",
                "phone": "+375 (29) 700-10-01",
                "email": "manager@demo.local",
                "work_calendar": "Пн-Пт: 09:00-17:00\nСб: консультации по записи\nВс: выходной",
                "note": "Отвечает за работу торгового зала, поставки и вопросы по обслуживанию.",
                "sort_order": 10,
                "image_color": (86, 126, 164),
            },
            {
                "full_name": "Петров Алексей Викторович",
                "slug": "petrov-aleksey-viktorovich",
                "position": "Фармацевт рецептурного отдела",
                "phone": "+375 (29) 700-10-02",
                "email": "rx@demo.local",
                "work_calendar": "Пн-Ср: 10:00-18:00\nЧт-Пт: 12:00-20:00\nСб-Вс: выходной",
                "note": "Помогает с наличием рецептурных препаратов и подбором аналогов по назначению врача.",
                "sort_order": 20,
                "image_color": (117, 140, 78),
            },
            {
                "full_name": "Смирнова Анна Игоревна",
                "slug": "smirnova-anna-igorevna",
                "position": "Консультант зала",
                "phone": "+375 (29) 700-10-03",
                "email": "help@demo.local",
                "work_calendar": "Пн-Пт: 11:00-19:00\nСб: 10:00-16:00\nВс: выходной",
                "note": "Подсказывает по навигации в каталоге, отделам и правилам оформления отзывов.",
                "sort_order": 30,
                "image_color": (165, 106, 130),
            },
        ]

        for spec in employee_specs:
            color = spec.pop("image_color")
            assert isinstance(color, tuple)
            slug = str(spec["slug"])
            defaults = {key: value for key, value in spec.items() if key != "slug"}
            employee, _created = EmployeeContact.objects.update_or_create(slug=slug, defaults=defaults)
            self._attach_required_image_if_missing(
                employee,
                field_name="photo",
                slug=slug,
                rgb=color,
            )

        self.stdout.write(self.style.NOTICE("✓ Публичные новости и контакты сотрудников обновлены"))
