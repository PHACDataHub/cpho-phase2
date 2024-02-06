# Generated by Django 4.1.9 on 2024-02-06 17:08

from django.db import migrations
import server.fields


class Migration(migrations.Migration):
    dependencies = [
        (
            "cpho",
            "0019_indicator_g1_indicator_g2_lower_indicator_g2_upper_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="benchmarking",
            name="standard_deviation",
        ),
        migrations.RemoveField(
            model_name="benchmarkinghistory",
            name="standard_deviation",
        ),
        migrations.RemoveField(
            model_name="indicator",
            name="benchmarking_legend",
        ),
        migrations.RemoveField(
            model_name="indicatorhistory",
            name="benchmarking_legend",
        ),
        migrations.AddField(
            model_name="indicator",
            name="table_title_age_2",
            field=server.fields.CharField(max_length=300, null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="table_title_province_territory_2",
            field=server.fields.CharField(max_length=300, null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="table_title_sex_2",
            field=server.fields.CharField(max_length=300, null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="title_age_2",
            field=server.fields.CharField(max_length=300, null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="title_province_territory_2",
            field=server.fields.CharField(max_length=300, null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="title_sex_2",
            field=server.fields.CharField(max_length=300, null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="table_title_age_2",
            field=server.fields.CharField(max_length=300, null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="table_title_province_territory_2",
            field=server.fields.CharField(max_length=300, null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="table_title_sex_2",
            field=server.fields.CharField(max_length=300, null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="title_age_2",
            field=server.fields.CharField(max_length=300, null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="title_province_territory_2",
            field=server.fields.CharField(max_length=300, null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="title_sex_2",
            field=server.fields.CharField(max_length=300, null=True),
        ),
        migrations.AddField(
            model_name="trendanalysis",
            name="data_point_lower_ci",
            field=server.fields.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="trendanalysis",
            name="data_point_upper_ci",
            field=server.fields.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="trendanalysis",
            name="data_quality",
            field=server.fields.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="trendanalysishistory",
            name="data_point_lower_ci",
            field=server.fields.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="trendanalysishistory",
            name="data_point_upper_ci",
            field=server.fields.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="trendanalysishistory",
            name="data_quality",
            field=server.fields.CharField(max_length=50, null=True),
        ),
    ]
