# Generated by Django 4.0.6 on 2022-07-13 00:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Indicator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=50)),
                ('topic', models.CharField(max_length=50)),
                ('indicator', models.CharField(max_length=50)),
                ('detailed_indicator', models.CharField(max_length=300)),
                ('sub_indicator_measurement', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='TrendAnalysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detailed_indicator', models.CharField(max_length=250)),
                ('year', models.SmallIntegerField()),
                ('data_point', models.FloatField()),
                ('line_of_best_fit_point', models.FloatField()),
                ('indicator', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='app.indicator')),
            ],
        ),
        migrations.CreateModel(
            name='IndicatorData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(max_length=50)),
                ('geography', models.CharField(max_length=50)),
                ('sex', models.CharField(max_length=50)),
                ('gender', models.CharField(max_length=50)),
                ('age_group', models.CharField(max_length=50)),
                ('age_group_type', models.CharField(max_length=50)),
                ('data_quality', models.CharField(max_length=50)),
                ('value', models.FloatField()),
                ('value_lower_bound', models.FloatField()),
                ('value_upper_bound', models.FloatField()),
                ('value_unit', models.CharField(max_length=50)),
                ('single_year_timeframe', models.CharField(max_length=50)),
                ('multi_year_timeframe', models.CharField(max_length=50)),
                ('indicator', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='app.indicator')),
            ],
        ),
        migrations.CreateModel(
            name='Benchmarking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detailed_indicator', models.CharField(max_length=150)),
                ('value_unit', models.CharField(max_length=100)),
                ('oced_country', models.CharField(max_length=100)),
                ('value', models.FloatField(max_length=50)),
                ('year', models.SmallIntegerField()),
                ('standard_deviation', models.FloatField()),
                ('comparison_to_oecd_avg', models.CharField(max_length=50)),
                ('indicator', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='app.indicator')),
            ],
        ),
    ]
