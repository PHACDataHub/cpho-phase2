# Generated by Django 4.1.9 on 2023-09-20 17:59

from django.db import migrations
from django.core.management import call_command

from server.model_util import DevProdTestMigration


def up(apps, schema_editor):
    call_command("loaddata", "cpho/fixtures/periods.yaml")


def down(apps, schema_editor):
    Period = apps.get_model("cpho", "Period")
    Period.objects.all().delete()


class Migration(DevProdTestMigration):
    apply_in_dev = True
    apply_in_prod = True
    apply_in_tests = False

    dependencies = [
        ("cpho", "0007_alter_dimensionvalue_name_en_and_more"),
    ]

    operations = [migrations.RunPython(up, down)]
