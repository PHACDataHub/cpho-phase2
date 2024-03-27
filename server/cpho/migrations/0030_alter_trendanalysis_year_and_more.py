# Generated by Django 4.1.9 on 2024-03-25 20:12

from django.db import migrations
import server.fields


class Migration(migrations.Migration):
    dependencies = [
        ("cpho", "0029_trendanalysis_unit_trendanalysishistory_unit"),
    ]

    operations = [
        migrations.AlterField(
            model_name="trendanalysis",
            name="year",
            field=server.fields.CharField(default=9999, max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="trendanalysishistory",
            name="year",
            field=server.fields.CharField(default=9999, max_length=50),
            preserve_default=False,
        ),
    ]
