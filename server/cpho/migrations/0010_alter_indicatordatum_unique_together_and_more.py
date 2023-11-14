# Generated by Django 4.1.9 on 2023-11-14 16:26

from django.db import migrations
import server.fields


class Migration(migrations.Migration):
    dependencies = [
        ("cpho", "0009_indicator_relevant_dimensions_and_more"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="indicatordatum",
            unique_together={
                ("indicator", "period", "dimension_type", "dimension_value")
            },
        ),
        migrations.AddField(
            model_name="indicatordatum",
            name="deletion_time",
            field=server.fields.CharField(
                default="", max_length=50, null=True
            ),
        ),
        migrations.AddField(
            model_name="indicatordatum",
            name="is_deleted",
            field=server.fields.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="indicatordatumhistory",
            name="deletion_time",
            field=server.fields.CharField(
                default="", max_length=50, null=True
            ),
        ),
        migrations.AddField(
            model_name="indicatordatumhistory",
            name="is_deleted",
            field=server.fields.BooleanField(default=False),
        ),
        migrations.AlterUniqueTogether(
            name="indicatordatum",
            unique_together={
                ("indicator", "period", "dimension_type", "dimension_value"),
                (
                    "indicator",
                    "period",
                    "dimension_type",
                    "literal_dimension_val",
                    "is_deleted",
                    "deletion_time",
                ),
            },
        ),
    ]
