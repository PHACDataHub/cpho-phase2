# Generated by Django 4.1.9 on 2024-01-23 21:21

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "cpho",
            "0014_indicatordirectory_indicatordirectoryuseraccess_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="phacorgrole",
            name="phac_org",
        ),
        migrations.RemoveField(
            model_name="phacorgrole",
            name="user",
        ),
        migrations.RemoveField(
            model_name="indicator",
            name="PHACOrg",
        ),
        migrations.RemoveField(
            model_name="indicatorhistory",
            name="PHACOrg",
        ),
        migrations.DeleteModel(
            name="PHACOrg",
        ),
        migrations.DeleteModel(
            name="PhacOrgRole",
        ),
    ]
