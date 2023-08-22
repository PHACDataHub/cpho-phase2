# Generated by Django 4.1.9 on 2023-08-22 18:18

from django.db import migrations
import server.fields


class Migration(migrations.Migration):
    dependencies = [
        ("cpho", "0006_phacorg_phacorgrole_indicator_phacorg_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="indicator",
            old_name="sub_category",
            new_name="topic",
        ),
        migrations.RenameField(
            model_name="indicatorhistory",
            old_name="sub_category",
            new_name="topic",
        ),
        migrations.AddField(
            model_name="indicatordatum",
            name="age_group_type",
            field=server.fields.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="indicatordatum",
            name="pt_data_availability",
            field=server.fields.CharField(max_length=75, null=True),
        ),
        migrations.AddField(
            model_name="indicatordatum",
            name="value_displayed",
            field=server.fields.CharField(max_length=75, null=True),
        ),
        migrations.AddField(
            model_name="indicatordatumhistory",
            name="age_group_type",
            field=server.fields.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="indicatordatumhistory",
            name="pt_data_availability",
            field=server.fields.CharField(max_length=75, null=True),
        ),
        migrations.AddField(
            model_name="indicatordatumhistory",
            name="value_displayed",
            field=server.fields.CharField(max_length=75, null=True),
        ),
        migrations.AlterField(
            model_name="indicatordatum",
            name="data_quality",
            field=server.fields.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="indicatordatum",
            name="value_unit",
            field=server.fields.CharField(max_length=75),
        ),
        migrations.AlterField(
            model_name="indicatordatumhistory",
            name="data_quality",
            field=server.fields.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="indicatordatumhistory",
            name="value_unit",
            field=server.fields.CharField(max_length=75),
        ),
    ]
