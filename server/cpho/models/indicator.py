from django.db import models

from server import fields
from server.model_util import (
    add_to_admin,
    track_versions_with_editor_and_submission,
)

from cpho.text import tdt, tm
from cpho.util import get_lang_code

from .model_util import SubmissionHelpersMixin, SubmissionQueryset


@add_to_admin
@track_versions_with_editor_and_submission
class Indicator(models.Model, SubmissionHelpersMixin):

    class Meta:
        verbose_name = tm("indicator")
        verbose_name_plural = tm("indicators")

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

    sdg_goal = fields.RichTextField(config_name="notes", null=True, blank=True)
    sdg_goal_fr = fields.RichTextField(
        config_name="notes", null=True, blank=True
    )

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

    # GRADE
    title_grade = fields.TextField(null=True, blank=True)
    title_grade_fr = fields.TextField(null=True, blank=True)

    table_title_grade = fields.TextField(null=True, blank=True)
    table_title_grade_fr = fields.TextField(null=True, blank=True)

    # HOSPITAL SETTING
    title_hospital_setting = fields.TextField(null=True, blank=True)
    title_hospital_setting_fr = fields.TextField(null=True, blank=True)

    table_title_hospital_setting = fields.TextField(null=True, blank=True)
    table_title_hospital_setting_fr = fields.TextField(null=True, blank=True)

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

    y_axis_trend_min = fields.FloatField(null=True, blank=True)
    y_axis_trend_max = fields.FloatField(null=True, blank=True)

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

    @property
    def bilingual_name(self):
        if get_lang_code() == "fr" and self.name_fr:
            return self.name_fr + ""
        return self.name + ""

    def __str__(self):
        return self.bilingual_name

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
