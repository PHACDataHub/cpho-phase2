# Generated by Django 5.0.6 on 2024-08-16 20:05

import server.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("cpho", "0041_alter_trendanalysis_data_point_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="indicator",
            name="benchmarking_dynamic_text",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="benchmarking_dynamic_text_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="benchmarking_footnotes_fr",
            field=server.fields.RichTextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="benchmarking_sources_fr",
            field=server.fields.RichTextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="detailed_indicator_fr",
            field=server.fields.CharField(max_length=300, null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="general_footnotes_fr",
            field=server.fields.RichTextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="impact_text_fr",
            field=server.fields.RichTextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="main_source_fr",
            field=server.fields.RichTextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="measure_text_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="name_fr",
            field=server.fields.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="other_relevant_sources_fr",
            field=server.fields.RichTextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="pt_dynamic_text_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="recommendations_for_hso_fr",
            field=server.fields.RichTextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="sub_indicator_measurement_fr",
            field=server.fields.CharField(max_length=150, null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="table_title_age_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="table_title_benchmark_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="table_title_education_household_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="table_title_income_quintiles_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="table_title_living_arrangement_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="table_title_overall_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="table_title_province_territory_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="table_title_sex_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="table_title_trend_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="title_age_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="title_benchmark_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="title_education_household_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="title_income_quintiles_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="title_living_arrangement_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="title_overall_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="title_province_territory_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="title_sex_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="title_trend_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="trend_footnotes_fr",
            field=server.fields.RichTextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="visual_description_trend_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="x_axis_benchmark_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="x_axis_trend_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicator",
            name="y_axis_trend_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="benchmarking_dynamic_text",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="benchmarking_dynamic_text_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="benchmarking_footnotes_fr",
            field=server.fields.RichTextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="benchmarking_sources_fr",
            field=server.fields.RichTextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="detailed_indicator_fr",
            field=server.fields.CharField(max_length=300, null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="general_footnotes_fr",
            field=server.fields.RichTextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="impact_text_fr",
            field=server.fields.RichTextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="main_source_fr",
            field=server.fields.RichTextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="measure_text_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="name_fr",
            field=server.fields.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="other_relevant_sources_fr",
            field=server.fields.RichTextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="pt_dynamic_text_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="recommendations_for_hso_fr",
            field=server.fields.RichTextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="sub_indicator_measurement_fr",
            field=server.fields.CharField(max_length=150, null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="table_title_age_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="table_title_benchmark_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="table_title_education_household_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="table_title_income_quintiles_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="table_title_living_arrangement_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="table_title_overall_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="table_title_province_territory_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="table_title_sex_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="table_title_trend_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="title_age_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="title_benchmark_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="title_education_household_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="title_income_quintiles_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="title_living_arrangement_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="title_overall_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="title_province_territory_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="title_sex_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="title_trend_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="trend_footnotes_fr",
            field=server.fields.RichTextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="visual_description_trend_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="x_axis_benchmark_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="x_axis_trend_fr",
            field=server.fields.TextField(null=True),
        ),
        migrations.AddField(
            model_name="indicatorhistory",
            name="y_axis_trend_fr",
            field=server.fields.TextField(null=True),
        ),
    ]
