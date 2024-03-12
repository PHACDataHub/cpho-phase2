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


# indicator_columns = []
class IndicatorSheetWriter(AbstractSheetWriter):
    sheet_name = "indicator"

    def get_column_configs(self):
        model = self.iterator.model

        fields_to_write = model._meta.fields
        return [
            ModelColumn(model, field.name)
            for field in fields_to_write
            if field.name != "relevant_period_types"
        ]


class IndicatorDatumSheetWriter(ModelToSheetWriter):
    sheet_name = "indicator_data"


class BenchmarkingSheetWriter(ModelToSheetWriter):
    pass


class TrendSheetWriter(ModelToSheetWriter):
    pass


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
