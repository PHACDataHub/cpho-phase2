import csv

from django.http import HttpResponse
from django.utils.functional import cached_property
from django.views.generic import View

from phac_aspc.rules import test_rule

from cpho.mapping_util import ExportMapper
from cpho.models import Indicator, IndicatorDatum

from .view_util import MustPassAuthCheckMixin


class ExportIndicator(MustPassAuthCheckMixin, View):
    def check_rule(self):
        return test_rule(
            "can_export_indicator",
            self.request.user,
            self.indicator,
        )

    @cached_property
    def indicator(self):
        if "pk" in self.kwargs:
            return Indicator.objects.get(pk=self.kwargs["pk"])
        else:
            return None

    def get(self, request, *args, **kwargs):
        indicator = self.indicator

        filename = "indicator_template"
        if indicator:
            # remove commas to avoid issues with csv
            filename = str(indicator.name).replace(",", "")

        response = HttpResponse(
            content_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}.csv"
            },
        )

        writer = csv.writer(response)
        header_row = [
            "Category",
            "Topic",
            "Indicator",
            "Detailed Indicator",
            "Sub_Indicator_Measurement",
            "Data_Quality",
            "Value",
            "Value_LowerCI",
            "Value_UpperCI",
            "Value_Displayed",
            "SingleYear_TimeFrame",
            "MultiYear_TimeFrame",
            "Dimension_Type",
            "Dimension_Value",
            "Period",
            "Reason_for_Null_Data",
            "Value_Units",
            "Arrow_Flag",
        ]
        writer.writerow(header_row)

        if self.indicator:
            for record in IndicatorDatum.active_objects.filter(
                indicator=self.indicator
            ):
                if record.dimension_type.is_literal:
                    deduced_dimension_value = record.literal_dimension_val
                else:
                    deduced_dimension_value = ExportMapper.map_dimension_value(
                        record.dimension_value
                    )

                writer.writerow(
                    [
                        ExportMapper.map_category(indicator.category),
                        ExportMapper.map_topic(indicator.topic),
                        indicator.name,
                        indicator.detailed_indicator,
                        indicator.sub_indicator_measurement,
                        ExportMapper.map_data_quality(record.data_quality),
                        record.value,
                        record.value_lower_bound,
                        record.value_upper_bound,
                        ExportMapper.map_value_displayed(
                            record.value_displayed
                        ),
                        record.single_year_timeframe,
                        record.multi_year_timeframe,
                        ExportMapper.map_dimension_type(record.dimension_type),
                        deduced_dimension_value,
                        record.period.code,
                        ExportMapper.map_reason_for_null(
                            record.reason_for_null
                        ),
                        ExportMapper.map_value_unit(record.value_unit),
                        ExportMapper.map_arrow_flag(record.arrow_flag),
                    ]
                )

        return response
