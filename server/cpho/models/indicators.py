from django.apps import apps
from django.db import models

from pleasant_promises.dataloader import SingletonDataLoader

from server import fields
from server.model_util import (
    add_to_admin,
    track_versions_with_editor,
    track_versions_with_editor_and_submission,
)

from cpho.constants import SUBMISSION_STATUSES
from cpho.text import tdt


@add_to_admin
@track_versions_with_editor
class Indicator(models.Model):
    CATEGORY_CHOICES = [
        ("", "--"),
        ("factors_influencing_health", tdt("Factors Influencing Health")),
        ("general_health_status", tdt("General Health Status")),
        ("health_outcomes", tdt("Health Outcomes")),
    ]

    TOPIC_CHOICES = [
        ("", "--"),
        (
            "childhood_and_family_factors",
            tdt("Childhood and Family Factors"),
        ),
        ("social_factors", tdt("Social Factors")),
        ("substance_use", tdt("Substance Use")),
        ("health_status", tdt("Health Status")),
        (
            "chronic_diseases_and_mental_health",
            tdt("Chronic Diseases and Mental Health"),
        ),
        ("communicable_diseases", tdt("Communicable Diseases")),
    ]

    name = fields.CharField(max_length=50)

    category = fields.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        verbose_name=tdt("Category"),
    )

    topic = fields.CharField(
        max_length=50,
        choices=TOPIC_CHOICES,
        verbose_name=tdt("Topic"),
    )

    detailed_indicator = fields.CharField(max_length=300)

    sub_indicator_measurement = fields.CharField(max_length=150)

    def __str__(self):
        return " ".join(
            [
                str(self.name),
            ]
        )


class IndicatorDatumQueryset(models.QuerySet):
    def with_last_version_date(self):
        last_version_date = models.Subquery(
            self.model._history_class.objects.filter(
                eternal_id=models.OuterRef("pk")
            )
            .order_by("-timestamp")
            .values("timestamp")[:1]
        )
        return self.annotate(last_version_date=last_version_date)

    def with_last_version_username(self, date_field="timestamp"):
        last_version_edited_by_username = models.Subquery(
            self.model._history_class.objects.filter(
                eternal_id=models.OuterRef("pk")
            )
            .order_by("-timestamp")
            .values("edited_by__username")[:1]
        )
        return self.annotate(
            last_version_edited_by_username=last_version_edited_by_username
        )

    def with_last_version_id(self):
        last_version_id = models.Subquery(
            self.model._history_class.objects.filter(
                eternal_id=models.OuterRef("pk")
            )
            .order_by("-timestamp")
            .values("id")[:1]
        )
        return self.annotate(last_version_id=last_version_id)

    def with_last_program_submitted_version_id(self):
        last_submitted_version_id = models.Subquery(
            self.model._history_class.objects.filter(
                eternal_id=models.OuterRef("pk"),
                is_program_submitted=True,
            )
            .order_by("-timestamp")
            .values("id")[:1]
        )
        return self.annotate(
            last_program_submitted_version_id=last_submitted_version_id
        )

    def with_last_submitted_version_id(self):
        last_submitted_version_id = models.Subquery(
            self.model._history_class.objects.filter(
                eternal_id=models.OuterRef("pk"),
                is_hso_submitted=True,
                is_program_submitted=True,
            )
            .order_by("-timestamp")
            .values("id")[:1]
        )
        return self.annotate(
            last_submitted_version_id=last_submitted_version_id
        )

    def with_submission_annotations(self):
        return (
            self.with_last_version_id()
            .with_last_submitted_version_id()
            .with_last_program_submitted_version_id()
        )


class IndicatorDatumChangelogNameLoader(SingletonDataLoader):
    @staticmethod
    def get_name(datum):
        if datum.dimension_type.is_literal:
            return f"{datum.indicator} ({datum.period}) {datum.dimension_type}: {datum.literal_dimension_val}"

        return f"{datum.indicator} ({datum.period}) {datum.dimension_type}: {datum.dimension_value}"

    def batch_load(self, datum_ids):
        IndicatorDatum = apps.get_model("cpho", "IndicatorDatum")

        data = IndicatorDatum.objects.filter(
            id__in=datum_ids
        ).prefetch_related(
            "indicator", "dimension_value", "dimension_type", "period"
        )
        by_id = {datum.id: datum for datum in data}
        return [self.get_name(by_id[x]) for x in datum_ids]


@add_to_admin
@track_versions_with_editor_and_submission
class IndicatorDatum(models.Model):
    objects = models.Manager.from_queryset(IndicatorDatumQueryset)()
    changelog_live_name_loader_class = IndicatorDatumChangelogNameLoader

    class Meta:
        unique_together = [
            ("indicator", "period", "dimension_type", "dimension_value"),
            ("indicator", "period", "dimension_type", "literal_dimension_val"),
        ]

    indicator = fields.ForeignKey(
        Indicator, null=False, on_delete=models.RESTRICT, related_name="data"
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

    LIVING_ARRANGMENT_CHOICES = [
        ("", "--"),
        ("all_living", tdt("All Living Arrangements")),
        ("couple_no_child", tdt("Couple no children")),
        (
            "couple_with_child",
            tdt("Couple with child(ren) less than 18 years old"),
        ),
        ("female_alone", tdt("Female living alone")),
        (
            "female_with_child",
            tdt("Female lone parent with child(ren) less than 18 years old"),
        ),
        ("male_alone", tdt("Male living alone")),
        (
            "male_with_child",
            tdt("Male lone parent with child(ren) less than 18 years old"),
        ),
        ("other_living", tdt("Other livng arrangments")),
    ]

    living_arrangement = pt_data_availability = fields.CharField(
        max_length=75, choices=LIVING_ARRANGMENT_CHOICES, null=True
    )

    DATA_QUALITY_CHOICES = [
        ("", "--"),
        ("caution", tdt("Caution")),
        ("acceptable", tdt("Acceptable")),
        ("good", tdt("Good")),
        ("suppressed", tdt("Suppressed")),
        ("excellent", tdt("Excellent")),
    ]

    data_quality = fields.CharField(
        max_length=50,
        choices=DATA_QUALITY_CHOICES,
        verbose_name=tdt("Data Quality"),
        null=True,
    )

    PT_DATA_AVAILABILITY_CHOICES = [
        ("", "--"),
        ("available", tdt("Available")),
        ("suppressed", tdt("Suppressed")),
        ("not_available", tdt("Not available")),
    ]

    pt_data_availability = fields.CharField(
        max_length=75, choices=PT_DATA_AVAILABILITY_CHOICES, null=True
    )

    value = fields.FloatField(null=True)

    value_lower_bound = fields.FloatField(null=True)

    value_upper_bound = fields.FloatField(null=True)

    VALUE_UNIT_CHOICES = [
        ("", tdt("--")),
        ("%", tdt("%")),
        ("per_100k", tdt("Per 100K")),
        ("years", tdt("Years")),
        ("per_100k_census", tdt("Per 100K census inhabitants")),
        ("per_100k_patient_days", tdt("Per 100K patient days")),
        ("per_100k_live_births", tdt("Per 100K live births")),
        ("other", tdt("Other")),
    ]

    value_unit = fields.CharField(
        max_length=50,
        choices=VALUE_UNIT_CHOICES,
        verbose_name=tdt("Value Unit"),
    )

    value_displayed = fields.CharField(max_length=50, null=True)

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

    @property
    def submission_status(self):
        try:
            self.last_version_id
            self.last_submitted_version_id
            self.last_program_submitted_version_id
        except AttributeError:
            raise Exception("You must add the submission_annotations")

        if not self.last_program_submitted_version_id:
            return SUBMISSION_STATUSES.NOT_YET_SUBMITTED

        if self.last_version_id == self.last_submitted_version_id:
            return SUBMISSION_STATUSES.SUBMITTED

        if self.last_version_id == self.last_program_submitted_version_id:
            return SUBMISSION_STATUSES.PROGRAM_SUBMITTED

        return SUBMISSION_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION


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
