from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.utils.functional import cached_property
from django.views import View

import openpyxl
from data_fetcher import cache_within_request
from phac_aspc.django.excel import (
    AbstractExportView,
    AbstractSheetWriter,
    ChoiceColumn,
    Column,
    CustomColumn,
    ModelColumn,
    ModelToSheetWriter,
)
from phac_aspc.rules import test_rule

from cpho.models import (
    Benchmarking,
    BenchmarkingHistory,
    Indicator,
    IndicatorDatum,
    IndicatorDatumHistory,
    IndicatorHistory,
    TrendAnalysis,
    TrendAnalysisHistory,
)
from cpho.util import get

indicator_columns = [
    CustomColumn("id", lambda x: x.eternal_id),
    ModelColumn(IndicatorHistory, "name"),
    ModelColumn(IndicatorHistory, "name_fr"),
    ChoiceColumn(IndicatorHistory, "category"),
    ChoiceColumn(IndicatorHistory, "topic"),
    ModelColumn(IndicatorHistory, "detailed_indicator"),
    ModelColumn(IndicatorHistory, "detailed_indicator_fr"),
    ModelColumn(IndicatorHistory, "sub_indicator_measurement"),
    ModelColumn(IndicatorHistory, "sub_indicator_measurement_fr"),
    ModelColumn(IndicatorHistory, "measure_text"),
    ModelColumn(IndicatorHistory, "measure_text_fr"),
    ModelColumn(IndicatorHistory, "title_overall"),
    ModelColumn(IndicatorHistory, "title_overall_fr"),
    ModelColumn(IndicatorHistory, "table_title_overall"),
    ModelColumn(IndicatorHistory, "table_title_overall_fr"),
    ModelColumn(IndicatorHistory, "sdg_goal"),
    ModelColumn(IndicatorHistory, "sdg_goal_fr"),
    ModelColumn(IndicatorHistory, "impact_text"),
    ModelColumn(IndicatorHistory, "impact_text_fr"),
    ModelColumn(IndicatorHistory, "general_footnotes"),
    ModelColumn(IndicatorHistory, "general_footnotes_fr"),
    ModelColumn(IndicatorHistory, "main_source_english"),
    ModelColumn(IndicatorHistory, "main_source_fr"),
    ModelColumn(IndicatorHistory, "other_relevant_sources_english"),
    ModelColumn(IndicatorHistory, "other_relevant_sources_fr"),
    ModelColumn(IndicatorHistory, "title_sex"),
    ModelColumn(IndicatorHistory, "title_sex_fr"),
    ModelColumn(IndicatorHistory, "table_title_sex"),
    ModelColumn(IndicatorHistory, "table_title_sex_fr"),
    ModelColumn(IndicatorHistory, "title_age"),
    ModelColumn(IndicatorHistory, "title_age_fr"),
    ModelColumn(IndicatorHistory, "table_title_age"),
    ModelColumn(IndicatorHistory, "table_title_age_fr"),
    ModelColumn(IndicatorHistory, "title_province_territory"),
    ModelColumn(IndicatorHistory, "title_province_territory_fr"),
    ModelColumn(IndicatorHistory, "table_title_province_territory"),
    ModelColumn(IndicatorHistory, "table_title_province_territory_fr"),
    ModelColumn(IndicatorHistory, "pt_dynamic_text"),
    ModelColumn(IndicatorHistory, "pt_dynamic_text_fr"),
    ModelColumn(IndicatorHistory, "title_living_arrangement"),
    ModelColumn(IndicatorHistory, "title_living_arrangement_fr"),
    ModelColumn(IndicatorHistory, "table_title_living_arrangement"),
    ModelColumn(IndicatorHistory, "table_title_living_arrangement_fr"),
    ModelColumn(IndicatorHistory, "title_education_household"),
    ModelColumn(IndicatorHistory, "title_education_household_fr"),
    ModelColumn(IndicatorHistory, "table_title_education_household"),
    ModelColumn(IndicatorHistory, "table_title_education_household_fr"),
    ModelColumn(IndicatorHistory, "title_income_quintiles"),
    ModelColumn(IndicatorHistory, "title_income_quintiles_fr"),
    ModelColumn(IndicatorHistory, "table_title_income_quintiles"),
    ModelColumn(IndicatorHistory, "table_title_income_quintiles_fr"),
    ModelColumn(IndicatorHistory, "title_trend"),
    ModelColumn(IndicatorHistory, "title_trend_fr"),
    ModelColumn(IndicatorHistory, "table_title_trend"),
    ModelColumn(IndicatorHistory, "table_title_trend_fr"),
    ModelColumn(IndicatorHistory, "visual_description_trend"),
    ModelColumn(IndicatorHistory, "visual_description_trend_fr"),
    ModelColumn(IndicatorHistory, "x_axis_trend"),
    ModelColumn(IndicatorHistory, "x_axis_trend_fr"),
    ModelColumn(IndicatorHistory, "y_axis_trend"),
    ModelColumn(IndicatorHistory, "y_axis_trend_fr"),
    ModelColumn(IndicatorHistory, "y_axis_trend_min"),
    ModelColumn(IndicatorHistory, "y_axis_trend_max"),
    ModelColumn(IndicatorHistory, "trend_footnotes"),
    ModelColumn(IndicatorHistory, "trend_footnotes_fr"),
    ModelColumn(IndicatorHistory, "title_benchmark"),
    ModelColumn(IndicatorHistory, "title_benchmark_fr"),
    ModelColumn(IndicatorHistory, "table_title_benchmark"),
    ModelColumn(IndicatorHistory, "table_title_benchmark_fr"),
    ModelColumn(IndicatorHistory, "x_axis_benchmark"),
    ModelColumn(IndicatorHistory, "x_axis_benchmark_fr"),
    ModelColumn(IndicatorHistory, "benchmarking_dynamic_text"),
    ModelColumn(IndicatorHistory, "benchmarking_dynamic_text_fr"),
    ModelColumn(IndicatorHistory, "benchmarking_footnotes"),
    ModelColumn(IndicatorHistory, "benchmarking_footnotes_fr"),
    ModelColumn(IndicatorHistory, "benchmarking_sources_english"),
    ModelColumn(IndicatorHistory, "benchmarking_sources_fr"),
    # quintiles
    ModelColumn(IndicatorHistory, "g1"),
    ModelColumn(IndicatorHistory, "g2_lower"),
    ModelColumn(IndicatorHistory, "g2_upper"),
    ModelColumn(IndicatorHistory, "g3_lower"),
    ModelColumn(IndicatorHistory, "g3_upper"),
    ModelColumn(IndicatorHistory, "g4_lower"),
    ModelColumn(IndicatorHistory, "g4_upper"),
    ModelColumn(IndicatorHistory, "g5"),
]

indicator_data_columns = [
    CustomColumn("id", lambda x: x.eternal_id),
    CustomColumn(
        "indicator_id",
        lambda x: x.indicator_id,
    ),
    # indicator columns useful to help identify??
    CustomColumn(
        "indicator name",
        lambda x: ExportHelpers.get_submitted_indicator_by_eternal_id(
            x.indicator_id
        ).name,
    ),
    CustomColumn(
        "detailed indicator",
        lambda x: ExportHelpers.get_submitted_indicator_by_eternal_id(
            x.indicator_id
        ).detailed_indicator,
    ),
    CustomColumn(
        "sub indicator measurement",
        lambda x: ExportHelpers.get_submitted_indicator_by_eternal_id(
            x.indicator_id
        ).sub_indicator_measurement,
    ),
    # denormalized periods, they'll probably only use year
    CustomColumn("year", lambda x: x.period.year),
    CustomColumn("year - quarter", lambda x: x.period.quarter),
    CustomColumn("year - type", lambda x: x.period.year_type),
    # denormalized dimension attrs
    CustomColumn("dimension_code", lambda x: x.dimension_type_id),
    CustomColumn("dimension_en", lambda x: x.dimension_type.name_en),
    CustomColumn("dimension_fr", lambda x: x.dimension_type.name_fr),
    CustomColumn(
        "is_dropdown_choice", lambda x: not (x.dimension_type.is_literal)
    ),
    CustomColumn(
        "dimension_value_en",
        lambda x: get(x, "dimension_value.name_en"),
    ),
    CustomColumn(
        "dimension_value_fr",
        lambda x: get(x, "dimension_value.name_fr"),
    ),
    CustomColumn(
        "literal_dimension_val", lambda x: x.literal_dimension_val or ""
    ),
    # value columns
    ChoiceColumn(IndicatorDatumHistory, "data_quality"),
    ChoiceColumn(IndicatorDatumHistory, "reason_for_null"),
    ModelColumn(IndicatorDatumHistory, "value"),
    ModelColumn(IndicatorDatumHistory, "value_lower_bound"),
    ModelColumn(IndicatorDatumHistory, "value_upper_bound"),
    ChoiceColumn(IndicatorDatumHistory, "value_unit"),
    ChoiceColumn(IndicatorDatumHistory, "value_displayed"),
    ModelColumn(IndicatorDatumHistory, "single_year_timeframe"),
    ModelColumn(IndicatorDatumHistory, "multi_year_timeframe"),
    ModelColumn(IndicatorDatumHistory, "arrow_flag"),
]

benchmarking_columns = [
    CustomColumn("id", lambda x: x.eternal_id),
    CustomColumn("indicator_id", lambda x: x.indicator_id),
    # indicator columns useful to help identify??
    CustomColumn(
        "indicator name",
        lambda x: ExportHelpers.get_submitted_indicator_by_eternal_id(
            x.indicator_id
        ).name,
    ),
    CustomColumn(
        "detailed indicator",
        lambda x: ExportHelpers.get_submitted_indicator_by_eternal_id(
            x.indicator_id
        ).detailed_indicator,
    ),
    CustomColumn(
        "sub indicator measurement",
        lambda x: ExportHelpers.get_submitted_indicator_by_eternal_id(
            x.indicator_id
        ).sub_indicator_measurement,
    ),
    ChoiceColumn(BenchmarkingHistory, "unit"),
    CustomColumn(
        "oecd_country",
        lambda x: get(x, "oecd_country.name_en"),
    ),
    ModelColumn(BenchmarkingHistory, "value"),
    ModelColumn(BenchmarkingHistory, "year"),
    ChoiceColumn(BenchmarkingHistory, "comparison_to_oecd_avg"),
    ChoiceColumn(BenchmarkingHistory, "labels"),
    CustomColumn(
        "Methodology differences",
        lambda x: "True" if x.methodology_differences else "False",
    ),
]

trend_columns = [
    CustomColumn("id", lambda x: x.eternal_id),
    CustomColumn("indicator_id", lambda x: x.indicator_id),
    # indicator columns useful to help identify??
    CustomColumn(
        "indicator name",
        lambda x: ExportHelpers.get_submitted_indicator_by_eternal_id(
            x.indicator_id
        ).name,
    ),
    CustomColumn(
        "detailed indicator",
        lambda x: ExportHelpers.get_submitted_indicator_by_eternal_id(
            x.indicator_id
        ).detailed_indicator,
    ),
    CustomColumn(
        "sub indicator measurement",
        lambda x: ExportHelpers.get_submitted_indicator_by_eternal_id(
            x.indicator_id
        ).sub_indicator_measurement,
    ),
    ModelColumn(TrendAnalysisHistory, "year"),
    ModelColumn(TrendAnalysisHistory, "data_point"),
    ModelColumn(TrendAnalysisHistory, "line_of_best_fit_point"),
    ModelColumn(TrendAnalysisHistory, "trend_segment"),
    ChoiceColumn(TrendAnalysisHistory, "trend"),
    ChoiceColumn(TrendAnalysisHistory, "data_quality"),
    ChoiceColumn(TrendAnalysisHistory, "unit"),
]


class ExportHelpers:
    @cache_within_request
    @staticmethod
    def get_submitted_indicator_ids():
        """
        Returns a list of indicator version ids that have been submitted
        """
        indicator_data = (
            Indicator.objects.all().with_last_submitted_version_id()
        ).order_by("name")
        indicator_version_ids = [
            x.last_submitted_version_id
            for x in indicator_data
            if x.last_submitted_version_id is not None
        ]
        return indicator_version_ids

    @classmethod
    @cache_within_request
    def get_submitted_indicators(cls):
        """
        Returns a list of indicator history objects that have been submitted
        """
        indicator_version_ids = cls.get_submitted_indicator_ids()
        return IndicatorHistory.objects.filter(
            pk__in=indicator_version_ids
        ).order_by("name")

    @classmethod
    @cache_within_request
    def get_submitted_indicator_dict_by_eternal_id(cls):
        all_submitted_indicators = cls.get_submitted_indicators()
        return {
            submitted_indicator.eternal_id: submitted_indicator
            for submitted_indicator in all_submitted_indicators
        }

    @classmethod
    def get_submitted_indicator_by_eternal_id(cls, eternal_id):
        return cls.get_submitted_indicator_dict_by_eternal_id()[eternal_id]

    @classmethod
    def get_submitted_data(cls):
        eternal_ids = [x.eternal_id for x in cls.get_submitted_indicators()]
        data = IndicatorDatum.objects.filter(
            indicator_id__in=eternal_ids, is_deleted=False
        ).with_last_submitted_version_id()
        version_ids = [
            x.last_submitted_version_id
            for x in data
            if x.last_submitted_version_id is not None
        ]
        submitted_data = (
            IndicatorDatumHistory.objects.filter(pk__in=version_ids)
            .select_related("period", "dimension_type", "dimension_value")
            .order_by("indicator_id", "period_id", "dimension_type_id")
        )
        return submitted_data

    @classmethod
    def get_submitted_benchmarking(cls):
        eternal_ids = [x.eternal_id for x in cls.get_submitted_indicators()]
        benchmarking_data = Benchmarking.objects.filter(
            # might not be necessary as benchmarking gets submitted with indicator but just in case
            indicator_id__in=eternal_ids,
            is_deleted=False,
        ).with_last_submitted_version_id()
        version_ids = [
            x.last_submitted_version_id
            for x in benchmarking_data
            if x.last_submitted_version_id is not None
        ]
        submitted_benchmarking = (
            BenchmarkingHistory.objects.filter(pk__in=version_ids)
            .select_related("indicator", "oecd_country")
            .order_by("indicator_id", "labels", "value")
        )
        return submitted_benchmarking

    @classmethod
    def get_submitted_trend_analysis(cls):
        eternal_ids = [x.eternal_id for x in cls.get_submitted_indicators()]
        trend_data = TrendAnalysis.objects.filter(
            # might not be necessary as trend gets submitted with indicator but just in case
            indicator_id__in=eternal_ids,
            is_deleted=False,
        ).with_last_submitted_version_id()
        version_ids = [
            x.last_submitted_version_id
            for x in trend_data
            if x.last_submitted_version_id is not None
        ]
        submitted_trend = (
            TrendAnalysisHistory.objects.filter(pk__in=version_ids)
            .select_related("indicator")
            .order_by("indicator_id", "year")
        )
        return submitted_trend


class IndicatorSheetWriter(ModelToSheetWriter):
    sheet_name = "indicator"
    columns = indicator_columns

    def get_queryset(self):
        data = ExportHelpers.get_submitted_indicators()
        return data


class IndicatorDatumSheetWriter(ModelToSheetWriter):
    sheet_name = "indicator_data"
    columns = indicator_data_columns

    def get_queryset(self):
        data = ExportHelpers.get_submitted_data()
        return data


class BenchmarkingSheetWriter(ModelToSheetWriter):
    columns = benchmarking_columns
    sheet_name = "benchmarking"

    def get_queryset(self):
        data = ExportHelpers.get_submitted_benchmarking()
        return data


class TrendSheetWriter(ModelToSheetWriter):
    columns = trend_columns
    sheet_name = "trend analysis"

    def get_queryset(self):
        data = ExportHelpers.get_submitted_trend_analysis()
        return data


class InfobaseExportView(View):
    @cached_property
    def workbook(self):
        return openpyxl.Workbook(write_only=True)

    def write_indicators(self):
        writer = IndicatorSheetWriter(workbook=self.workbook)
        writer.write()

    def write_indicator_data(self):
        writer = IndicatorDatumSheetWriter(
            workbook=self.workbook,
        )
        writer.write()

    def write_trends(self):
        writer = TrendSheetWriter(workbook=self.workbook)
        writer.write()

    def write_benchmarking(self):
        writer = BenchmarkingSheetWriter(workbook=self.workbook)
        writer.write()

    def get(self, request, *args, **kwargs):
        if not test_rule("is_admin_or_hso", request.user):
            raise PermissionDenied()

        self.write_indicators()
        self.write_indicator_data()
        self.write_trends()
        self.write_benchmarking()

        response = HttpResponse(
            headers={"Content-Type": "application/vnd.ms-excel"}
        )
        response[
            "Content-Disposition"
        ] = f"attachment; filename=hopic_infobase_export.xlsx"
        self.workbook.save(response)

        return response
