# Generated by Django 4.1.9 on 2023-11-29 20:21

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("cpho", "0012_benchmarking_country_benchmarkinghistory_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="indicator",
            name="general_footnotes",
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="general_footnotes",
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
    ]
