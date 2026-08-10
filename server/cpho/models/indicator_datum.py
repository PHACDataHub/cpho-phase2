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


class IndicatorDatumChangelogNameFetcher(DataFetcher):
    @staticmethod
    def get_name(datum):
        if datum.dimension_type.is_literal:
            return f"{datum.indicator} ({datum.period}) {datum.dimension_type}: {datum.literal_dimension_val}"

        return f"{datum.indicator} ({datum.period}) {datum.dimension_type}: {datum.dimension_value}"

    def batch_load_dict(self, datum_ids):
        data = IndicatorDatum.objects.filter(id__in=datum_ids).select_related(
            "indicator", "dimension_value", "dimension_type", "period"
        )
        by_id = {datum.id: datum for datum in data}
        return by_id


@add_to_admin
@track_versions_with_editor_and_submission
class IndicatorDatum(models.Model, SubmissionHelpersMixin):
    objects = models.Manager.from_queryset(SubmissionQueryset)()
    active_objects = ActiveObjManager.from_queryset(SubmissionQueryset)()
    changelog_live_name_fetcher_class = IndicatorDatumChangelogNameFetcher

    class Meta:

        verbose_name = tm("indicator_data")
        verbose_name_plural = tm("indicator_data")

        unique_together = [
            (
                "indicator",
                "period",
                "dimension_type",
                "dimension_value",
            ),
            (
                "indicator",
                "period",
                "dimension_type",
                "literal_dimension_val",
                "is_deleted",
                "deletion_time",
            ),
        ]

    indicator = fields.ForeignKey(
        Indicator, null=False, on_delete=models.CASCADE, related_name="data"
    )

    literal_dimension_val = fields.CharField(
        max_length=50, null=True, blank=True, default=None
    )

    period = fields.ForeignKey(
        # TODO: figure out if this should be null, default to current period or null w/out default
        "cpho.Period",
        null=True,
        blank=True,
        on_delete=models.RESTRICT,
    )

    DATA_QUALITY_CHOICES = [
        ("", "--"),
        ("caution", tm("caution")),
        ("acceptable", tm("acceptable")),
        ("good", tm("good")),
        ("suppressed", tm("suppressed")),
        ("very_good", tm("very_good")),
        ("excellent", tm("excellent")),
    ]

    data_quality = fields.CharField(
        max_length=50,
        choices=DATA_QUALITY_CHOICES,
        verbose_name=tm("data_quality"),
        null=True,
    )

    REASON_FOR_NULL_CHOICES = [
        ("", "--"),
        ("suppressed", tm("suppressed")),
        ("not_available", tm("not_available")),
    ]

    reason_for_null = fields.CharField(
        max_length=75, choices=REASON_FOR_NULL_CHOICES, null=True, default=""
    )

    value = fields.FloatField(null=True)

    value_lower_bound = fields.FloatField(null=True)

    value_upper_bound = fields.FloatField(null=True)

    VALUE_UNIT_CHOICES = [
        ("", "--"),
        ("daily_dose_1k_census", tm("daily_dose_1k_census")),
        ("percentage", tm("percentage")),
        ("rate_10k_patient_days", tm("rate_10k_patient_days")),
        ("rate_100k_age_standardized", tm("rate_100k_age_standardized")),
        ("rate_100k_age_specific_crude", tm("rate_100k_age_specific_crude")),
        ("rate_100k_crude", tm("rate_100k_crude")),
        ("rate_100k_live_births", tm("rate_100k_live_births")),
        ("years", tm("years")),
        ("litres", tm("litres")),
    ]

    value_unit = fields.CharField(
        max_length=75,
        choices=VALUE_UNIT_CHOICES,
        verbose_name=tm("value_unit"),
    )

    VALUE_DISPLAYED_CHOICES = [
        ("", "--"),
        ("%", "%"),
        ("per_1k_census", tm("per_1k_census")),
        ("per_10k_patient_days", tm("per_10k_patient_days")),
        ("per_100k_live_births", tm("per_100k_live_births")),
        ("per_100k_population", tm("per_100k_population")),
        ("per_100k_population_per_year", tm("per_100k_population_per_year")),
        ("years", tm("years")),
        ("litres", tm("litres")),
        ("other", tm("other")),
    ]

    value_displayed = fields.CharField(
        max_length=75,
        choices=VALUE_DISPLAYED_CHOICES,
        null=True,
    )

    single_year_timeframe = fields.CharField(max_length=50, null=True)

    multi_year_timeframe = fields.CharField(max_length=50, null=True)

    dimension_type = fields.ForeignKey(
        "cpho.DimensionType",
        null=False,
        blank=False,
        on_delete=models.RESTRICT,
    )

    dimension_value = fields.ForeignKey(
        "cpho.DimensionValue",
        null=True,
        blank=True,
        on_delete=models.RESTRICT,
    )

    ARROW_FLAG_CHOICES = [
        ("", "--"),
        ("up", "\u2191"),
        ("down", "\u2193"),
    ]

    arrow_flag = fields.CharField(max_length=50, null=True)

    is_deleted = fields.BooleanField(default=False)
    deletion_time = fields.CharField(
        max_length=50, blank=True, null=True, default=""
    )

    def __str__(self):
        return " ".join(
            [
                "dim_type:",
                str(self.dimension_type),
                "; dim_val:",
                str(self.dimension_value),
                "; Value:",
                str(self.value),
                "; literal_val:",
                str(self.literal_dimension_val),
            ]
        )
