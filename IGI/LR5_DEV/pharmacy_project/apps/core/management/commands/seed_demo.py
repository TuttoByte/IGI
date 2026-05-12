"""
Идемпотентное наполнение: две демо-учётные записи + каталог препаратов.

Запуск: python manage.py seed_demo
"""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import Profile, UserRole
from apps.pharmacy.models import Category, Department, Medication
from apps.suppliers.models import Supplier

DEMO_PASSWORD = "PharmaDemo2026!"


class Command(BaseCommand):
    help = "Создаёт demo_admin, demo_client и демо-каталог (если БД пустая по препаратам)."

    def handle(self, *args: object, **options: object) -> None:
        with transaction.atomic():
            self._seed_users()
            self._seed_catalog()
            self._seed_suppliers()
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

    def _seed_catalog(self) -> None:
        if Medication.objects.exists():
            self.stdout.write("· Каталог уже содержит препараты — пропуск наполнения")
            return

        cat_obez, _ = Category.objects.get_or_create(
            slug="obezbolivayushie",
            defaults={"name": "Обезболивающие", "description": "НПВС и анальгетики."},
        )
        cat_vit, _ = Category.objects.get_or_create(
            slug="vitaminy",
            defaults={"name": "Витамины и БАД", "description": "Поддержка иммунитета."},
        )
        dep_zal1, _ = Department.objects.get_or_create(
            slug="zal-1",
            defaults={"name": "Зал №1 (открытый доступ)", "floor": 1, "description": "Основная торговая зона."},
        )
        dep_zal2, _ = Department.objects.get_or_create(
            slug="zal-2",
            defaults={"name": "Зал №2 (рецептурный)", "floor": 2, "description": "Рецептурные препараты."},
        )

        today = date.today()
        meds: list[dict[str, object]] = [
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
                "category": cat_vit,
                "department": dep_zal2,
            },
        ]
        for data in meds:
            Medication.objects.create(**data)
        self.stdout.write(self.style.NOTICE(f"✓ Добавлено препаратов: {len(meds)}"))

    def _seed_suppliers(self) -> None:
        """Связывает демо-препараты с поставщиками (идемпотентно)."""
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
        codes = ["ASP-500-DEMO", "PAR-250-DEMO", "RX-AMOX-DEMO"]
        meds = list(Medication.objects.filter(code__in=codes))
        if not meds:
            self.stdout.write("· Нет демо-препаратов — связи поставщиков пропущены")
            return
        batch1 = [m for m in meds if m.code in ("ASP-500-DEMO", "PAR-250-DEMO")]
        if batch1:
            s1.medications.add(*batch1)
        batch2 = [m for m in meds if m.code == "RX-AMOX-DEMO"]
        if batch2:
            s2.medications.add(*batch2)
        self.stdout.write(self.style.NOTICE("✓ Связи поставщик ↔ препарат обновлены"))
