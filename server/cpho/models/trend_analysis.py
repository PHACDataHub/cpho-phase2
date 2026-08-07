from django.db import models

from data_fetcher.core import DataFetcher

from server import fields
from server.model_util import (
    add_to_admin,
    track_versions_with_editor_and_submission,
)

from cpho.text import tm

from .indicator import Indicator
from .model_util import (
    ActiveObjManager,
    SubmissionHelpersMixin,
    SubmissionQueryset,
)


class TrendRecordLiveNameFetcher(DataFetcher):
    def batch_load_dict(self, keys):
        data = TrendAnalysis.objects.filter(id__in=keys).prefetch_related(
            "indicator"
        )
        by_id = {datum.id: datum.__str__() for datum in data}
        return by_id


@add_to_admin
@track_versions_with_editor_and_submission
class TrendAnalysis(models.Model, SubmissionHelpersMixin):
    changelog_live_name_fetcher_class = TrendRecordLiveNameFetcher

    class Meta:
        unique_together = [
            (
                "indicator",
                "year",
                "is_deleted",
                "deletion_time",
            ),
        ]
        verbose_name = tm("trend_analysis")
        verbose_name_plural = tm("trend_analysis")

    objects = models.Manager.from_queryset(SubmissionQueryset)()
    active_objects = ActiveObjManager.from_queryset(SubmissionQueryset)()

    indicator = fields.ForeignKey(
        Indicator, on_delete=models.CASCADE, related_name="trend_analysis"
    )
    year = fields.CharField(max_length=50, null=True, blank=True)
    data_point = fields.FloatField(blank=True, null=True)
    line_of_best_fit_point = fields.FloatField(null=True, blank=True)
    trend_segment = fields.CharField(max_length=50, null=True, blank=True)

    TREND_CHOICES = [
        ("", "--"),
        ("stable", tm("stable")),
        ("increasing", tm("increasing")),
        ("decreasing", tm("decreasing")),
    ]
    trend = fields.CharField(
        max_length=50, choices=TREND_CHOICES, null=True, blank=True
    )
    UNIT_CHOICES = [
        ("", "--"),
        ("daily_dose_1k_census", tm("daily_dose_1k_census")),
        ("percentage", tm("percentage")),
        ("percent_age_standardized", tm("percent_age_standardized")),
        ("percentage_crude", tm("percentage_crude")),
        ("rate_10k_patient_days", tm("rate_10k_patient_days")),
        ("rate_100k_age_standardized", tm("rate_100k_age_standardized")),
        ("rate_100k_age_specific_crude", tm("rate_100k_age_specific_crude")),
        ("rate_100k_crude", tm("rate_100k_crude")),
        ("rate_100k_live_births", tm("rate_100k_live_births")),
        ("rate_100k_population_per_year", tm("rate_100k_population_per_year")),
        ("litres", tm("litres")),
        ("years", tm("years")),
        ("other", tm("other")),
    ]

    unit = fields.CharField(
        max_length=75,
        choices=UNIT_CHOICES,
        verbose_name=tm("value_unit"),
        blank=True,
        null=True,
    )
    DATA_QUALITY_CHOICES = [
        ("", "--"),
        ("caution", tm("caution")),
        ("good", tm("good")),
        ("very_good", tm("very_good")),
        ("excellent", tm("excellent")),
    ]
    data_quality = fields.CharField(
        max_length=50,
        choices=DATA_QUALITY_CHOICES,
        null=True,
        blank=True,
    )
    data_point_lower_ci = fields.FloatField(null=True, blank=True)
    data_point_upper_ci = fields.FloatField(null=True, blank=True)
    is_deleted = fields.BooleanField(default=False)
    deletion_time = fields.CharField(
        max_length=50, blank=True, null=True, default=""
    )

    ARROW_FLAG_CHOICES = [
        ("", "--"),
        ("up", "\u2191"),
        ("down", "\u2193"),
    ]

    arrow_flag = fields.CharField(max_length=50, null=True)

    def __str__(self):
        return "Trend: " + str(self.indicator) + " : " + str(self.year)


# the following commented-out models don't really do anything yet,

# class Benchmarking(models.Model):
#     indicator = fields.ForeignKey(Indicator, on_delete=models.RESTRICT)
#     detailed_indicator = fields.CharField(max_length=150)
#     value_unit = fields.CharField(max_length=100)
#     oced_country = fields.CharField(max_length=100)
#     value = fields.FloatField(max_length=50)
#     year = fields.IntegerField()
#     standard_deviation = fields.FloatField()
#     comparison_to_oecd_avg = fields.CharField(max_length=50)
#
#     def __str__(self):
#         return self.detailed_indicator
#
#
# class TrendAnalysis(models.Model):
#     indicator = fields.ForeignKey(Indicator, on_delete=models.RESTRICT)
#     detailed_indicator = fields.CharField(max_length=250)
#     year = fields.IntegerField()
#     data_point = fields.FloatField()
#     line_of_best_fit_point = fields.FloatField()
#
#     def __str__(self):
#         return self.detailed_indicator
#         return self.detailed_indicator
