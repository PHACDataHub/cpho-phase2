# Generated by Django 4.1.9 on 2023-11-27 20:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import server.fields


class Migration(migrations.Migration):
    dependencies = [
        ("cpho", "0011_merge_20231120_1253"),
    ]

    operations = [
        migrations.CreateModel(
            name="Benchmarking",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("value", server.fields.FloatField(max_length=50)),
                ("year", server.fields.IntegerField()),
                ("standard_deviation", server.fields.FloatField()),
                (
                    "comparison_to_oecd_avg",
                    server.fields.CharField(max_length=50),
                ),
                ("labels", server.fields.CharField(max_length=50, null=True)),
                ("is_deleted", server.fields.BooleanField(default=False)),
                (
                    "deletion_time",
                    server.fields.CharField(
                        default="", max_length=50, null=True
                    ),
                ),
                (
                    "indicator",
                    server.fields.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        to="cpho.indicator",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Country",
            fields=[
                (
                    "id",
                    models.CharField(
                        max_length=10, primary_key=True, serialize=False
                    ),
                ),
                ("name_en", server.fields.CharField(max_length=100)),
                (
                    "name_fr",
                    server.fields.CharField(max_length=100, null=True),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BenchmarkingHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "timestamp",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("value", server.fields.FloatField(max_length=50)),
                ("year", server.fields.IntegerField()),
                ("standard_deviation", server.fields.FloatField()),
                (
                    "comparison_to_oecd_avg",
                    server.fields.CharField(max_length=50),
                ),
                ("labels", server.fields.CharField(max_length=50, null=True)),
                ("is_deleted", server.fields.BooleanField(default=False)),
                (
                    "deletion_time",
                    server.fields.CharField(
                        default="", max_length=50, null=True
                    ),
                ),
                (
                    "edited_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "eternal",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="versions",
                        to="cpho.benchmarking",
                    ),
                ),
                (
                    "indicator",
                    server.fields.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="cpho.indicator",
                    ),
                ),
                (
                    "oecd_country",
                    server.fields.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="cpho.country",
                    ),
                ),
            ],
            options={
                "ordering": ["timestamp"],
                "get_latest_by": "timestamp",
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="benchmarking",
            name="oecd_country",
            field=server.fields.ForeignKey(
                on_delete=django.db.models.deletion.RESTRICT, to="cpho.country"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="benchmarking",
            unique_together={
                ("indicator", "oecd_country", "is_deleted", "deletion_time")
            },
        ),
    ]