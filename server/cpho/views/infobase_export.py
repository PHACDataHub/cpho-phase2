from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.utils.functional import cached_property
from django.views import View

import openpyxl
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

from cpho.models import Benchmarking, Indicator, IndicatorDatum, TrendAnalysis
from cpho.util import get

indicator_columns = [
    ModelColumn(Indicator, "id"),
    ModelColumn(Indicator, "name"),
    ChoiceColumn(Indicator, "category"),
    ChoiceColumn(Indicator, "topic"),
    ModelColumn(Indicator, "detailed_indicator"),
    ModelColumn(Indicator, "sub_indicator_measurement"),
    ModelColumn(Indicator, "measure_text"),
    ModelColumn(Indicator, "title_overall"),
    ModelColumn(Indicator, "table_title_overall"),
    ModelColumn(Indicator, "impact_text"),
    ModelColumn(Indicator, "general_footnotes"),
    ModelColumn(Indicator, "main_source_english"),
    ModelColumn(Indicator, "other_relevant_sources_english"),
    ModelColumn(Indicator, "title_sex"),
    ModelColumn(Indicator, "table_title_sex"),
    ModelColumn(Indicator, "title_sex_2"),
    ModelColumn(Indicator, "table_title_sex_2"),
    ModelColumn(Indicator, "title_age"),
    ModelColumn(Indicator, "table_title_age"),
    ModelColumn(Indicator, "title_age_2"),
    ModelColumn(Indicator, "table_title_age_2"),
    ModelColumn(Indicator, "title_province_territory"),
    ModelColumn(Indicator, "table_title_province_territory"),
    ModelColumn(Indicator, "title_province_territory_2"),
    ModelColumn(Indicator, "table_title_province_territory_2"),
    ModelColumn(Indicator, "title_living_arrangement"),
    ModelColumn(Indicator, "table_title_living_arrangement"),
    ModelColumn(Indicator, "title_education_household"),
    ModelColumn(Indicator, "table_title_education_household"),
    ModelColumn(Indicator, "title_income_quintiles"),
    ModelColumn(Indicator, "table_title_income_quintiles"),
    ModelColumn(Indicator, "title_trend"),
    ModelColumn(Indicator, "table_title_trend"),
    ModelColumn(Indicator, "visual_description_trend"),
    ModelColumn(Indicator, "x_axis_trend"),
    ModelColumn(Indicator, "y_axis_trend"),
    ModelColumn(Indicator, "trend_footnotes"),
    ModelColumn(Indicator, "title_benchmark"),
    ModelColumn(Indicator, "table_title_benchmark"),
    ModelColumn(Indicator, "x_axis_benchmark"),
    ModelColumn(Indicator, "benchmarking_footnotes"),
    ModelColumn(Indicator, "benchmarking_sources_english"),
    # quintiles
    ModelColumn(Indicator, "g1"),
    ModelColumn(Indicator, "g2_lower"),
    ModelColumn(Indicator, "g2_upper"),
    ModelColumn(Indicator, "g3_lower"),
    ModelColumn(Indicator, "g3_upper"),
    ModelColumn(Indicator, "g4_lower"),
    ModelColumn(Indicator, "g4_upper"),
    ModelColumn(Indicator, "g5"),
]


class IndicatorSheetWriter(AbstractSheetWriter):
    sheet_name = "indicator"

    def get_column_configs(self):
        return indicator_columns


indicator_data_columns = [
    ModelColumn(IndicatorDatum, "id"),
    CustomColumn("indicator_id", lambda x: x.indicator_id),
    # indicator columns useful to help identify??
    CustomColumn("indicator name", lambda x: x.indicator.name),
    CustomColumn(
        "detailed indicator", lambda x: x.indicator.detailed_indicator
    ),
    CustomColumn(
        "sub indicator measurement",
        lambda x: x.indicator.sub_indicator_measurement,
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
    ChoiceColumn(IndicatorDatum, "data_quality"),
    ChoiceColumn(IndicatorDatum, "reason_for_null"),
    ModelColumn(IndicatorDatum, "value"),
    ModelColumn(IndicatorDatum, "value_lower_bound"),
    ModelColumn(IndicatorDatum, "value_upper_bound"),
    ChoiceColumn(IndicatorDatum, "value_unit"),
    ChoiceColumn(IndicatorDatum, "value_displayed"),
    ModelColumn(IndicatorDatum, "single_year_timeframe"),
    ModelColumn(IndicatorDatum, "multi_year_timeframe"),
]


class IndicatorDatumSheetWriter(ModelToSheetWriter):
    sheet_name = "indicator_data"

    def get_column_configs(self):
        return indicator_data_columns


benchmarking_columns = [
    ModelColumn(IndicatorDatum, "id"),
    CustomColumn("indicator_id", lambda x: x.indicator_id),
    # indicator columns useful to help identify??
    CustomColumn("indicator name", lambda x: x.indicator.name),
    CustomColumn(
        "detailed indicator", lambda x: x.indicator.detailed_indicator
    ),
    CustomColumn(
        "sub indicator measurement",
        lambda x: x.indicator.sub_indicator_measurement,
    ),
    ChoiceColumn(Benchmarking, "unit"),
    ModelColumn(Benchmarking, "oecd_country"),
    ModelColumn(Benchmarking, "value"),
    ModelColumn(Benchmarking, "year"),
    ChoiceColumn(Benchmarking, "comparison_to_oecd_avg"),
    ChoiceColumn(Benchmarking, "labels"),
]


class BenchmarkingSheetWriter(ModelToSheetWriter):
    def get_column_configs(self):
        return benchmarking_columns


trend_columns = [
    ModelColumn(TrendAnalysis, "id"),
    ModelColumn(TrendAnalysis, "year"),
    ModelColumn(TrendAnalysis, "data_point"),
    ModelColumn(TrendAnalysis, "line_of_best_fit_point"),
    ModelColumn(TrendAnalysis, "trend_segment"),
    ChoiceColumn(TrendAnalysis, "trend"),
    ChoiceColumn(TrendAnalysis, "data_quality"),
]


class TrendSheetWriter(ModelToSheetWriter):
    def get_column_configs(self):
        return trend_columns


class InfobaseExportView(View):
    @cached_property
    def workbook(self):
        return openpyxl.Workbook(write_only=True)

    def write_indicators(self):
        # todo: use submitted indicators instead
        writer = IndicatorSheetWriter(
            workbook=self.workbook, iterator=Indicator.objects.all()
        )
        writer.write()

    def write_indicator_data(self):
        writer = IndicatorDatumSheetWriter(
            workbook=self.workbook, iterator=IndicatorDatum.objects.all()
        )
        writer.write()

    def write_trends(self):
        writer = TrendSheetWriter(
            workbook=self.workbook, iterator=TrendAnalysis.objects.all()
        )
        writer.write()

    def write_benchmarking(self):
        writer = BenchmarkingSheetWriter(
            workbook=self.workbook, iterator=Benchmarking.objects.all()
        )
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
        response["Content-Disposition"] = (
            f"attachment; filename=hopic_infobase_export.xlsx"
        )
        self.workbook.save(response)

        return response
