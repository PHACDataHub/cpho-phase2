# Generated by Django 4.1.9 on 2024-04-12 18:05

from django.db import migrations
import server.fields


class Migration(migrations.Migration):
    dependencies = [
        ("cpho", "0031_benchmarking_methodology_differences_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="indicator",
            name="pt_dynamic_text",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="recommendations_for_hso",
            field=server.fields.RichTextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="pt_dynamic_text",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="recommendations_for_hso",
            field=server.fields.RichTextField(null=True),
        ),
    ]
