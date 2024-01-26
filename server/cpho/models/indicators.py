from django.apps import apps
from django.db import models

from ckeditor.fields import RichTextField
from pleasant_promises.dataloader import SingletonDataLoader

from server import fields
from server.model_util import (
    add_to_admin,
    track_versions_with_editor,
    track_versions_with_editor_and_submission,
)

from cpho.constants import SUBMISSION_STATUSES
from cpho.text import tdt
from cpho.util import get_lang_code


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

    relevant_dimensions = fields.ManyToManyField(
        "cpho.DimensionType",
        blank=True,
        related_name="indicators",
    )

    # GENERAL
    measure_text = fields.CharField(max_length=300, null=True, blank=True)
    impact_text = fields.CharField(max_length=300, null=True, blank=True)
    title_overall = fields.CharField(max_length=300, null=True, blank=True)
    general_footnotes = RichTextField(
        config_name="notes", null=True, blank=True
    )
    main_source_english = RichTextField(
        config_name="notes", null=True, blank=True
    )
    other_relevant_sources_english = RichTextField(
        config_name="notes", null=True, blank=True
    )

    # SEX
    title_sex = fields.CharField(max_length=300, null=True, blank=True)
    table_title_sex = fields.CharField(max_length=300, null=True, blank=True)

    # AGE
    title_age = fields.CharField(max_length=300, null=True, blank=True)
    table_title_age = fields.CharField(max_length=300, null=True, blank=True)

    # PROVINCE/TERRITORY
    title_province_territory = fields.CharField(
        max_length=300, null=True, blank=True
    )
    table_title_province_territory = fields.CharField(
        max_length=300, null=True, blank=True
    )

    # LIVING ARRANGEMENT
    title_living_arrangement = fields.CharField(
        max_length=300, null=True, blank=True
    )
    table_title_living_arrangement = fields.CharField(
        max_length=300, null=True, blank=True
    )

    # EDUCATION HOUSEHOLD
    title_education_household = fields.CharField(
        max_length=300, null=True, blank=True
    )
    table_title_education_household = fields.CharField(
        max_length=300, null=True, blank=True
    )

    # INCOME QUINTILES
    title_income_quintiles = fields.CharField(
        max_length=300, null=True, blank=True
    )
    table_title_income_quintiles = fields.CharField(
        max_length=300, null=True, blank=True
    )

    # TREND
    title_trend = fields.CharField(max_length=300, null=True, blank=True)
    table_title_trend = fields.CharField(max_length=300, null=True, blank=True)
    visual_description_trend = fields.CharField(
        max_length=300, null=True, blank=True
    )
    x_axis_trend = fields.CharField(max_length=300, null=True, blank=True)
    y_axis_trend = fields.CharField(max_length=300, null=True, blank=True)
    trend_footnotes = RichTextField(config_name="notes", null=True, blank=True)

    # BENCHMARKING
    benchmarking_legend = fields.CharField(
        max_length=300, null=True, blank=True
    )
    title_benchmark = fields.CharField(max_length=300, null=True, blank=True)
    table_title_benchmark = fields.CharField(
        max_length=300, null=True, blank=True
    )
    x_axis_benchmark = fields.CharField(max_length=300, null=True, blank=True)
    benchmarking_footnotes = RichTextField(
        config_name="notes", null=True, blank=True
    )
    benchmarking_sources_english = RichTextField(
        config_name="notes", null=True, blank=True
    )

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


class ActiveIndicatorDatumManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


@add_to_admin
@track_versions_with_editor_and_submission
class IndicatorDatum(models.Model):
    objects = models.Manager.from_queryset(IndicatorDatumQueryset)()
    active_objects = ActiveIndicatorDatumManager.from_queryset(
        IndicatorDatumQueryset
    )()
    changelog_live_name_loader_class = IndicatorDatumChangelogNameLoader

    class Meta:
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

    DATA_QUALITY_CHOICES = [
        ("", "--"),
        ("caution", tdt("Caution")),
        ("acceptable", tdt("Acceptable")),
        ("good", tdt("Good")),
        ("suppressed", tdt("Suppressed")),
        ("very_good", tdt("Very Good")),
    ]

    data_quality = fields.CharField(
        max_length=50,
        choices=DATA_QUALITY_CHOICES,
        verbose_name=tdt("Data Quality"),
        null=True,
    )

    REASON_FOR_NULL_CHOICES = [
        ("", "--"),
        ("suppressed", tdt("Suppressed")),
        ("not_available", tdt("Not available")),
    ]

    reason_for_null = fields.CharField(
        max_length=75, choices=REASON_FOR_NULL_CHOICES, null=True, default=""
    )

    value = fields.FloatField(null=True)

    value_lower_bound = fields.FloatField(null=True)

    value_upper_bound = fields.FloatField(null=True)

    VALUE_UNIT_CHOICES = [
        ("", tdt("--")),
        ("age_rate", tdt("Age-Standardized Rate")),
        ("crude_rate", tdt("Crude Rate")),
        ("daily_dose_per_1k_census", tdt("Defined Daily Dose/1,000 Census")),
        ("percentage", tdt("Percentage")),
        ("percentage_crude_rate", tdt("Percentage (Crude Rate)")),
        ("rate_per_10k_patient", tdt("Rate per 10,000 Patient Days")),
        ("rate_per_100k", tdt("Rate per 100,000")),
        ("rate_per_100k_crude", tdt("Rate per 100,000 (Crude Rate)")),
        ("rate_per_100k_live_births", tdt("Rate per 100,000 Live Births")),
        ("years", tdt("years")),
        ("other", tdt("other")),
    ]

    value_unit = fields.CharField(
        max_length=75,
        choices=VALUE_UNIT_CHOICES,
        verbose_name=tdt("Value Unit"),
    )

    VALUE_DISPLAYED_CHOICES = [
        ("", tdt("--")),
        ("%", tdt("%")),
        ("per_1k_census", tdt("Per 1,000 census inhabitants")),
        ("per_10k_patient", tdt("Per 10,000 patient days")),
        ("per_100k", tdt("Per 100,000")),
        ("per_100k_live_births", tdt("Per 100,000 live births")),
        ("years", tdt("years")),
        ("other", tdt("other")),
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


class BenchmarkingManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


@add_to_admin
@track_versions_with_editor
class Benchmarking(models.Model):
    class Meta:
        unique_together = [
            (
                "indicator",
                "oecd_country",
                "is_deleted",
                "deletion_time",
                "labels",
            ),
        ]

    objects = models.Manager()
    active_objects = BenchmarkingManager()
    indicator = fields.ForeignKey(
        Indicator, on_delete=models.RESTRICT, related_name="benchmarking"
    )
    UNIT_CHOICES = [
        ("", "--"),
        (
            "age_standard_rate_per_100K",
            tdt("Age standardized rates per 100 000 population"),
        ),
        ("age_standard_percentage", tdt("Age-standardized percentage")),
        ("ddd_per_1000_per_day", tdt("DDD per 1000 population per day")),
        (
            "deaths_per_million_inhabitants",
            tdt("Deaths per million inhabitants"),
        ),
        ("incidence_100K_population", tdt("Incidence per 100 000 population")),
        ("litres_per_capita", tdt("Litres per Capita")),
        ("percent", tdt("Percent")),
        ("percent_children", tdt("Percent of children")),
        (
            "percent_births_below_2500_grams",
            tdt("Percent of live births below 2500 grams"),
        ),
        (
            "percent_people_fully_vaccinated",
            tdt("Percent of people fully vaccinated"),
        ),
        ("percent_population", tdt("Percent of population")),
        (
            "percent_population_health_good_or_very_good",
            tdt(
                "Percent of population that rate their health as good or very good"
            ),
        ),
        ("percentage_value", tdt("Percentage value")),
        ("rate_per_100K", tdt("Rate per 100 000")),
        ("rate_per_100K_population", tdt("Rate per 100 000 population")),
        ("rate_per_1000_population", tdt("Rate per 1000 population")),
        ("total_deaths_per_1M", tdt("Total deaths per 1 million")),
        ("total_per_100K_persons", tdt("Total per 100 000 persons")),
    ]
    unit = fields.CharField(max_length=50, null=True, choices=UNIT_CHOICES)
    oecd_country = fields.ForeignKey("cpho.Country", on_delete=models.RESTRICT)
    value = fields.FloatField(max_length=50)
    year = fields.IntegerField()
    standard_deviation = fields.FloatField(null=True)

    COMPARISON_CHOICES = [
        ("", "--"),
        ("better", tdt("Better")),
        ("similar", tdt("Similar")),
        ("worse", tdt("Worse")),
        ("outlier", tdt("Outlier")),
    ]
    comparison_to_oecd_avg = fields.CharField(
        max_length=50, choices=COMPARISON_CHOICES
    )

    LABEL_CHOICES = [
        ("", "--"),
        ("anxiety", tdt("Anxiety")),
        ("depression", tdt("Depression")),
        ("women", tdt("Women")),
        ("men", tdt("Men")),
    ]
    labels = fields.CharField(max_length=50, null=True, choices=LABEL_CHOICES)
    is_deleted = fields.BooleanField(default=False)
    deletion_time = fields.CharField(
        max_length=50, blank=True, null=True, default=""
    )

    def __str__(self):
        return str(self.indicator) + " : " + str(self.oecd_country)


class TrendAnalysisManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


@add_to_admin
@track_versions_with_editor
class TrendAnalysis(models.Model):
    class Meta:
        unique_together = [
            (
                "indicator",
                "year",
                "is_deleted",
                "deletion_time",
            ),
        ]

    objects = models.Manager()
    active_objects = TrendAnalysisManager()
    indicator = fields.ForeignKey(
        Indicator, on_delete=models.RESTRICT, related_name="trend_analysis"
    )
    year = fields.CharField(max_length=50)
    year_range = fields.CharField(max_length=50, null=True, blank=True)
    data_point = fields.FloatField()
    line_of_best_fit_point = fields.FloatField(null=True, blank=True)
    trend_segment = fields.CharField(max_length=50, null=True, blank=True)

    TREND_CHOICES = [
        ("", "--"),
        ("stable", tdt("Stable")),
        ("increasing", tdt("Increasing")),
        ("decreasing", tdt("Decreasing")),
    ]
    trend = fields.CharField(max_length=50, null=True, blank=True)
    is_deleted = fields.BooleanField(default=False)
    deletion_time = fields.CharField(
        max_length=50, blank=True, null=True, default=""
    )

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
