# Generated manually for apps.reviews (Review model)

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("pharmacy", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Review",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "rating",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(5),
                        ],
                        verbose_name="оценка",
                    ),
                ),
                ("text", models.TextField(blank=True, verbose_name="текст")),
                (
                    "moderation_status",
                    models.CharField(
                        choices=[
                            ("PENDING", "На модерации"),
                            ("APPROVED", "Опубликован"),
                            ("REJECTED", "Отклонён"),
                        ],
                        db_index=True,
                        default="PENDING",
                        max_length=20,
                        verbose_name="модерация",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="создано")),
                (
                    "medication",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="pharmacy.medication",
                        verbose_name="препарат",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="автор",
                    ),
                ),
            ],
            options={
                "verbose_name": "отзыв",
                "verbose_name_plural": "отзывы",
                "ordering": ("-created_at",),
                "indexes": [
                    models.Index(fields=["medication", "moderation_status", "-created_at"], name="reviews_rev_med_md_crd_idx"),
                    models.Index(fields=["medication", "moderation_status", "-rating"], name="reviews_rev_med_md_rt_idx"),
                    models.Index(fields=["user", "-created_at"], name="reviews_rev_usr_crd_idx"),
                ],
                "constraints": [
                    models.UniqueConstraint(fields=("user", "medication"), name="reviews_unique_user_medication"),
                ],
            },
        ),
    ]
