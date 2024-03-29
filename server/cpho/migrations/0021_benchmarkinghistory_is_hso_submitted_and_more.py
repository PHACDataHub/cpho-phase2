# Generated by Django 4.1.9 on 2024-02-16 15:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import server.fields


class Migration(migrations.Migration):
    dependencies = [
        ("cpho", "0020_remove_benchmarking_standard_deviation_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="benchmarkinghistory",
            name="is_hso_submitted",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="benchmarkinghistory",
            name="is_program_submitted",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="is_hso_submitted",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="is_program_submitted",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="trendanalysishistory",
            name="is_hso_submitted",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="trendanalysishistory",
            name="is_program_submitted",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="IndicatorMetaDataSubmission",
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
                    "submission_type",
                    models.CharField(
                        choices=[
                            ("hso", "HSO"),
                            ("program", "Surveillance Program"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "indicator",
                    server.fields.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cpho.indicator",
                    ),
                ),
                (
                    "submitted_by",
                    server.fields.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
