# Generated by Django 4.1.9 on 2024-06-04 11:43

from django.db import migrations
from django.db.models import F


def flip_incorrect_upper_lower_trend(apps, schema_editor):
    # for the TrendAnalysis model, flip the data_point_upper_ci and data_point_lower_ci values where the data_point_upper_ci is less than the data_point_lower_ci
    TrendAnalysis = apps.get_model("cpho", "TrendAnalysis")
    incorrect_trends = TrendAnalysis.objects.filter(
        data_point_upper_ci__lt=F("data_point_lower_ci")
    )
    print("Correcting ", incorrect_trends.count(), " incorrect trends")
    print("Correcting ", incorrect_trends)
    for trend in incorrect_trends:
        corrected_upper_ci = trend.data_point_lower_ci
        corrected_lower_ci = trend.data_point_upper_ci
        # use .update() to avoid triggering signals
        TrendAnalysis.objects.filter(pk=trend.pk).update(
            data_point_upper_ci=corrected_upper_ci,
            data_point_lower_ci=corrected_lower_ci,
        )

    # for TrendAnalysisHistory model, flip the data_point_upper_ci and data_point_lower_ci values where the data_point_upper_ci is less than the data_point_lower_ci
    TrendAnalysisHistory = apps.get_model("cpho", "TrendAnalysisHistory")
    incorrect_trend_history = TrendAnalysisHistory.objects.filter(
        data_point_upper_ci__lt=F("data_point_lower_ci")
    )
    print(
        "Correcting ",
        incorrect_trend_history.count(),
        " incorrect trend histories",
    )
    print("Correcting ", incorrect_trend_history)
    for trend_history in incorrect_trend_history:
        corrected_upper_ci = trend_history.data_point_lower_ci
        corrected_lower_ci = trend_history.data_point_upper_ci
        # use .update() to avoid triggering signals
        TrendAnalysisHistory.objects.filter(pk=trend_history.pk).update(
            data_point_upper_ci=corrected_upper_ci,
            data_point_lower_ci=corrected_lower_ci,
        )

    # check if the flip was successful
    incorrect_trends = TrendAnalysis.objects.filter(
        data_point_upper_ci__lt=F("data_point_lower_ci")
    )
    if incorrect_trends.count() > 0:
        raise ValueError("Failed to flip the incorrect trends")
    incorrect_trend_history = TrendAnalysisHistory.objects.filter(
        data_point_upper_ci__lt=F("data_point_lower_ci")
    )
    if incorrect_trend_history.count() > 0:
        raise ValueError("Failed to flip the incorrect trend histories")


def no_op(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("cpho", "0038_remove_indicator_table_title_age_2_and_more"),
    ]

    operations = [
        migrations.RunPython(flip_incorrect_upper_lower_trend, no_op),
    ]
