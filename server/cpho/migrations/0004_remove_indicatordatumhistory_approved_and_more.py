# Generated by Django 4.1.9 on 2023-07-24 20:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import server.fields


class Migration(migrations.Migration):
    dependencies = [
        ("cpho", "0003_alter_indicatordatum_unique_together"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="indicatordatumhistory",
            name="approved",
        ),
        migrations.AddField(
            model_name="indicatordatumhistory",
            name="is_hso_submitted",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="indicatordatumhistory",
            name="is_program_submitted",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="IndicatorDataSubmission",
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
                    "dimension_type",
                    server.fields.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="cpho.dimensiontype",
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
                    "period",
                    server.fields.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="cpho.period",
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