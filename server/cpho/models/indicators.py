from django.apps import apps
from django.db import models

from data_fetcher.core import DataFetcher
from pleasant_promises.dataloader import SingletonDataLoader

from server import fields
from server.model_util import (
    add_to_admin,
    track_versions_with_editor,
    track_versions_with_editor_and_submission,
)

from cpho.constants import SUBMISSION_STATUSES
from cpho.text import tdt, tm
from cpho.util import get_lang_code


class SubmissionQueryset(models.QuerySet):
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
        last_program_submitted_version_id = models.Subquery(
            self.model._history_class.objects.filter(
                eternal_id=models.OuterRef("pk"),
                is_program_submitted=True,
            )
            .order_by("-timestamp")
            .values("id")[:1]
        )
        return self.annotate(
            last_program_submitted_version_id=last_program_submitted_version_id
        )

    def with_last_submitted_version_id(self):
        last_submitted_version_id = models.Subquery(
            self.model._history_class.objects.filter(
                eternal_id=models.OuterRef("pk"),
                is_hso_submitted=True,
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


class SubmissionHelpersMixin:
    def submission_status(self, submission_type):
        try:
            self.last_version_id
            self.last_submitted_version_id
            self.last_program_submitted_version_id
        except AttributeError:
            raise Exception("You must add the submission_annotations")

        if submission_type == "hso":
            if not self.last_submitted_version_id:
                return SUBMISSION_STATUSES.NOT_YET_SUBMITTED
            if self.last_version_id == self.last_submitted_version_id:
                return SUBMISSION_STATUSES.SUBMITTED
        elif submission_type == "program":
            if not self.last_program_submitted_version_id:
                return SUBMISSION_STATUSES.NOT_YET_SUBMITTED
            if self.last_version_id == self.last_program_submitted_version_id:
                return SUBMISSION_STATUSES.PROGRAM_SUBMITTED

        return SUBMISSION_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION


@add_to_admin
@track_versions_with_editor_and_submission
class Indicator(models.Model, SubmissionHelpersMixin):
    excluded_diff_fields = ["relevant_period_types"]
    objects = models.Manager.from_queryset(SubmissionQueryset)()
    CATEGORY_CHOICES = [
        ("", "--"),
        ("factors_influencing_health", tm("factors_influencing_health")),
        ("general_health_status", tdt("General Health Status")),
        ("health_outcomes", tm("health_outcomes")),
    ]

    TOPIC_CHOICES = [
        ("", "--"),
        ("childhood_and_family_factors", tm("childhood_and_family_factors")),
        ("social_factors", tm("social_factors")),
        ("substance_use", tm("substance_use")),
        ("health_status", tm("health_status")),
        (
            "chronic_diseases_and_mental_health",
            tm("chronic_diseases_and_mental_health"),
        ),
        ("communicable_diseases", tm("communicable_diseases")),
    ]

    PERIOD_TYPE_CHOICES = [
        ("calendar_years", tm("calendar_year")),
        ("fiscal_years", tm("fiscal_year")),
        ("fiscal_quarters", tm("fiscal_quarters")),
    ]

    name = fields.CharField(max_length=50)
    name_fr = fields.CharField(max_length=100, null=True, blank=True)

    category = fields.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        verbose_name=tm("category"),
    )

    topic = fields.CharField(
        max_length=50,
        choices=TOPIC_CHOICES,
        verbose_name=tm("topic"),
    )

    detailed_indicator = fields.CharField(max_length=300)
    detailed_indicator_fr = fields.CharField(
        max_length=300, null=True, blank=True
    )

    sub_indicator_measurement = fields.CharField(max_length=150)
    sub_indicator_measurement_fr = fields.CharField(
        max_length=150, null=True, blank=True
    )

    relevant_dimensions = fields.ManyToManyField(
        "cpho.DimensionType",
        blank=True,
        related_name="indicators",
    )

    relevant_period_types = fields.CommaSeparatedCharField(
        choices=PERIOD_TYPE_CHOICES,
        max_length=250,
        blank=True,
    )

    # GENERAL
    measure_text = fields.TextField(null=True, blank=True)
    measure_text_fr = fields.TextField(null=True, blank=True)

    title_overall = fields.TextField(null=True, blank=True)
    title_overall_fr = fields.TextField(null=True, blank=True)

    table_title_overall = fields.TextField(null=True, blank=True)
    table_title_overall_fr = fields.TextField(null=True, blank=True)

    impact_text = fields.RichTextField(
        config_name="notes", null=True, blank=True
    )
    impact_text_fr = fields.RichTextField(
        config_name="notes", null=True, blank=True
    )

    general_footnotes = fields.RichTextField(
        config_name="notes", null=True, blank=True
    )
    general_footnotes_fr = fields.RichTextField(
        config_name="notes", null=True, blank=True
    )

    main_source_english = fields.RichTextField(
        config_name="notes", null=True, blank=True
    )
    main_source_fr = fields.RichTextField(
        config_name="notes", null=True, blank=True
    )

    other_relevant_sources_english = fields.RichTextField(
        config_name="notes", null=True, blank=True
    )
    other_relevant_sources_fr = fields.RichTextField(
        config_name="notes", null=True, blank=True
    )

    # SEX
    title_sex = fields.TextField(null=True, blank=True)
    title_sex_fr = fields.TextField(null=True, blank=True)

    table_title_sex = fields.TextField(null=True, blank=True)
    table_title_sex_fr = fields.TextField(null=True, blank=True)

    # AGE
    title_age = fields.TextField(null=True, blank=True)
    title_age_fr = fields.TextField(null=True, blank=True)

    table_title_age = fields.TextField(null=True, blank=True)
    table_title_age_fr = fields.TextField(null=True, blank=True)

    # PROVINCE/TERRITORY
    title_province_territory = fields.TextField(null=True, blank=True)
    title_province_territory_fr = fields.TextField(null=True, blank=True)

    table_title_province_territory = fields.TextField(null=True, blank=True)
    table_title_province_territory_fr = fields.TextField(null=True, blank=True)

    pt_dynamic_text = fields.TextField(null=True, blank=True)
    pt_dynamic_text_fr = fields.TextField(null=True, blank=True)

    # LIVING ARRANGEMENT
    title_living_arrangement = fields.TextField(null=True, blank=True)
    title_living_arrangement_fr = fields.TextField(null=True, blank=True)

    table_title_living_arrangement = fields.TextField(null=True, blank=True)
    table_title_living_arrangement_fr = fields.TextField(null=True, blank=True)

    # EDUCATION HOUSEHOLD
    title_education_household = fields.TextField(null=True, blank=True)
    title_education_household_fr = fields.TextField(null=True, blank=True)

    table_title_education_household = fields.TextField(null=True, blank=True)
    table_title_education_household_fr = fields.TextField(
        null=True, blank=True
    )

    # INCOME QUINTILES
    title_income_quintiles = fields.TextField(null=True, blank=True)
    title_income_quintiles_fr = fields.TextField(null=True, blank=True)

    table_title_income_quintiles = fields.TextField(null=True, blank=True)
    table_title_income_quintiles_fr = fields.TextField(null=True, blank=True)

    # TREND
    title_trend = fields.TextField(null=True, blank=True)
    title_trend_fr = fields.TextField(null=True, blank=True)

    table_title_trend = fields.TextField(null=True, blank=True)
    table_title_trend_fr = fields.TextField(null=True, blank=True)

    visual_description_trend = fields.TextField(null=True, blank=True)
    visual_description_trend_fr = fields.TextField(null=True, blank=True)

    x_axis_trend = fields.TextField(null=True, blank=True)
    x_axis_trend_fr = fields.TextField(null=True, blank=True)

    y_axis_trend = fields.TextField(null=True, blank=True)
    y_axis_trend_fr = fields.TextField(null=True, blank=True)

    trend_footnotes = fields.RichTextField(
        config_name="notes", null=True, blank=True
    )
    trend_footnotes_fr = fields.RichTextField(
        config_name="notes", null=True, blank=True
    )

    # BENCHMARKING
    # benchmarking_legend = fields.CharField(
    #     max_length=300, null=True, blank=True
    # )
    title_benchmark = fields.TextField(null=True, blank=True)
    title_benchmark_fr = fields.TextField(null=True, blank=True)

    table_title_benchmark = fields.TextField(null=True, blank=True)
    table_title_benchmark_fr = fields.TextField(null=True, blank=True)

    x_axis_benchmark = fields.TextField(null=True, blank=True)
    x_axis_benchmark_fr = fields.TextField(null=True, blank=True)

    benchmarking_dynamic_text = fields.TextField(null=True, blank=True)
    benchmarking_dynamic_text_fr = fields.TextField(null=True, blank=True)

    benchmarking_footnotes = fields.RichTextField(
        config_name="notes", null=True, blank=True
    )
    benchmarking_footnotes_fr = fields.RichTextField(
        config_name="notes", null=True, blank=True
    )

    benchmarking_sources_english = fields.RichTextField(
        config_name="notes", null=True, blank=True
    )
    benchmarking_sources_fr = fields.RichTextField(
        config_name="notes", null=True, blank=True
    )

    # QUINTILES
    # very small/technical audience, not worth translating vb-names)
    g1 = fields.FloatField(null=True, blank=True, verbose_name="G1")
    g2_lower = fields.FloatField(
        null=True, blank=True, verbose_name="G2 lower"
    )
    g2_upper = fields.FloatField(
        null=True, blank=True, verbose_name="G2 upper"
    )
    g3_lower = fields.FloatField(
        null=True, blank=True, verbose_name="G3 lower"
    )
    g3_upper = fields.FloatField(
        null=True, blank=True, verbose_name="G3 upper"
    )
    g4_lower = fields.FloatField(
        null=True, blank=True, verbose_name="G4 lower"
    )
    g4_upper = fields.FloatField(
        null=True, blank=True, verbose_name="G4 upper"
    )
    g5 = fields.FloatField(null=True, blank=True, verbose_name="G5")

    recommendations_for_hso = fields.RichTextField(
        config_name="notes", null=True, blank=True
    )
    recommendations_for_hso_fr = fields.RichTextField(
        config_name="notes", null=True, blank=True
    )

    def __str__(self):
        return " ".join(
            [
                str(self.name),
            ]
        )

    def get_relevant_periods(self):
        # filter Period. to years that have data or have the same type as the indicator's relevant_period_types
        from .lookups import Period

        globally_relevant = Period.get_currently_relevant_periods()
        return self._filter_irrelevant_periods(globally_relevant)

    def get_adjacent_periods(self):
        from .lookups import Period

        globally_relevant = Period.get_currently_relevant_periods()
        min_year = min([x.year for x in globally_relevant])
        max_year = max([x.year for x in globally_relevant])
        adjacent_periods = Period.objects.filter(
            year__lte=max_year + 2, year__gte=min_year - 2
        )
        adjacent_periods = set(adjacent_periods) - set(globally_relevant)
        return self._filter_irrelevant_periods(adjacent_periods)

    def _filter_irrelevant_periods(self, periods):
        # if there isn't a "preference" set, return all relevant periods
        from .lookups import Period

        if not self.relevant_period_types:
            return periods

        relevant = []
        for period in periods:
            if (
                period.quarter
                and "fiscal_quarters" in self.relevant_period_types
            ):
                relevant.append(period)
            elif (
                period.year_type == Period.FISCAL_YEAR_TYPE
                and period.quarter is None
                and "fiscal_years" in self.relevant_period_types
            ):
                relevant.append(period)
            elif (
                period.year_type == Period.CALENDAR_YEAR_TYPE
                and period.quarter is None
                and "calendar_years" in self.relevant_period_types
            ):
                relevant.append(period)

        return relevant


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


class ActiveObjManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


@add_to_admin
@track_versions_with_editor_and_submission
class IndicatorDatum(models.Model, SubmissionHelpersMixin):
    objects = models.Manager.from_queryset(SubmissionQueryset)()
    active_objects = ActiveObjManager.from_queryset(SubmissionQueryset)()
    changelog_live_name_fetcher_class = IndicatorDatumChangelogNameFetcher

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
        ("percent_age_standardized", tm("percent_age_standardized")),
        ("percentage_crude", tm("percentage_crude")),
        ("rate_10k_patient_days", tm("rate_10k_patient_days")),
        ("rate_100k_age_standardized", tm("rate_100k_age_standardized")),
        ("rate_100k_age_specific_crude", tm("rate_100k_age_specific_crude")),
        ("rate_100k_crude", tm("rate_100k_crude")),
        ("rate_100k_live_births", tm("rate_100k_live_births")),
        ("rate_100k_population_per_year", tm("rate_100k_population_per_year")),
        ("years", tm("years")),
        ("litres", tm("litres")),
        ("other", tm("other")),
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


class BenchmarkLiveNameFetcher(DataFetcher):
    """
    changelog won't prefetch related fields
    so we define a live-name fetcher
    """

    def batch_load_dict(self, keys):
        data = Benchmarking.objects.filter(id__in=keys).prefetch_related(
            "indicator", "oecd_country"
        )
        by_id = {datum.id: datum.__str__() for datum in data}
        return by_id


@add_to_admin
@track_versions_with_editor_and_submission
class Benchmarking(models.Model, SubmissionHelpersMixin):
    changelog_live_name_fetcher_class = BenchmarkLiveNameFetcher

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

    objects = models.Manager.from_queryset(SubmissionQueryset)()
    active_objects = ActiveObjManager.from_queryset(SubmissionQueryset)()
    indicator = fields.ForeignKey(
        Indicator, on_delete=models.CASCADE, related_name="benchmarking"
    )
    UNIT_CHOICES = [
        ("", "--"),
        ("age_standard_rate_per_100k", tm("age_standard_rate_per_100k")),
        ("age_standard_percentage", tm("age_standard_percentage")),
        ("ddd_per_1000_per_day", tm("ddd_per_1000_per_day")),
        (
            "deaths_per_million_inhabitants",
            tm("deaths_per_million_inhabitants"),
        ),
        ("incidence_100k_population", tm("incidence_100k_population")),
        ("litres_per_capita", tm("litres_per_capita")),
        ("percent", tm("percent")),
        ("percent_children", tm("percent_children")),
        (
            "percent_births_below_2500_grams",
            tm("percent_births_below_2500_grams"),
        ),
        (
            "percent_people_fully_vaccinated",
            tm("percent_people_fully_vaccinated"),
        ),
        ("percent_population", tm("percent_population")),
        (
            "percent_population_health_good_or_very_good",
            tm("percent_population_health_good_or_very_good"),
        ),
        ("percentage_value", tm("percentage_value")),
        ("rate_per_100k", tm("rate_per_100k")),
        ("rate_per_100k_population", tm("rate_per_100k_population")),
        ("rate_per_1000_population", tm("rate_per_1000_population")),
        ("total_deaths_per_1m", tm("total_deaths_per_1m")),
        ("total_per_100k_persons", tm("total_per_100k_persons")),
        ("litres_per_person", tm("litres_per_person")),
        ("years", tm("years")),
    ]
    unit = fields.CharField(
        max_length=50, choices=UNIT_CHOICES, blank=True, null=True
    )
    oecd_country = fields.ForeignKey(
        "cpho.Country", on_delete=models.RESTRICT, blank=True, null=True
    )
    value = fields.FloatField(blank=True, null=True)
    year = fields.CharField(max_length=50, blank=True, null=True)
    # standard_deviation = fields.FloatField(null=True)

    COMPARISON_CHOICES = [
        ("", "--"),
        ("better", tm("better")),
        ("similar", tm("similar")),
        ("worse", tm("worse")),
        ("outlier", tm("outlier")),
    ]
    comparison_to_oecd_avg = fields.CharField(
        max_length=50, choices=COMPARISON_CHOICES, blank=True, null=True
    )

    LABEL_CHOICES = [
        ("", "--"),
        ("anxiety", tm("anxiety")),
        ("depression", tm("depression")),
        ("women", tm("women")),
        ("men", tm("men")),
    ]
    labels = fields.CharField(
        max_length=50, blank=True, null=True, choices=LABEL_CHOICES
    )
    methodology_differences = fields.BooleanField(default=False)
    is_deleted = fields.BooleanField(default=False)
    deletion_time = fields.CharField(
        max_length=50, blank=True, null=True, default=""
    )

    def __str__(self):
        return str(self.indicator) + " : " + str(self.oecd_country)


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
