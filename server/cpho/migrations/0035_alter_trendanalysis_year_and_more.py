# Generated by Django 4.1.9 on 2024-05-01 20:45

from django.db import migrations
import server.fields


class Migration(migrations.Migration):
    dependencies = [
        ("cpho", "0034_period_is_current_periodhistory_is_current"),
    ]

    operations = [
        migrations.AlterField(
            model_name="trendanalysis",
            name="year",
            field=server.fields.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="trendanalysishistory",
            name="year",
            field=server.fields.CharField(max_length=50, null=True),
        ),
    ]
