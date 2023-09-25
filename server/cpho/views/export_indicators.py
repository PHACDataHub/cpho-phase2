import csv

from django.http import HttpResponse
from django.utils.functional import cached_property
from django.views.generic import View

from server.rules_framework import test_rule

from cpho.models import Indicator, IndicatorDatum
from cpho.views.view_util import export_mapper

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
        ]
        writer.writerow(header_row)

        if self.indicator:
            mapper = export_mapper()
            for record in IndicatorDatum.objects.filter(
                indicator=self.indicator
            ):
                if record.dimension_type.is_literal:
                    deduced_dimension_value = record.literal_dimension_val
                else:
                    deduced_dimension_value = mapper[
                        "non_literal_dimension_value_mapper"
                    ].get(record.dimension_value, "")
                writer.writerow(
                    [
                        mapper["category_mapper"].get(indicator.category, ""),
                        mapper["topic_mapper"].get(indicator.topic, ""),
                        indicator.name,
                        indicator.detailed_indicator,
                        indicator.sub_indicator_measurement,
                        mapper["data_quality_mapper"].get(
                            record.data_quality, ""
                        ),
                        record.value,
                        record.value_lower_bound,
                        record.value_upper_bound,
                        mapper["value_displayed_mapper"].get(
                            record.value_displayed, ""
                        ),
                        record.single_year_timeframe,
                        record.multi_year_timeframe,
                        mapper["dimension_type_mapper"].get(
                            record.dimension_type, ""
                        ),
                        deduced_dimension_value,
                        record.period.code,
                        mapper["reason_for_null_mapper"].get(
                            record.reason_for_null, ""
                        ),
                        mapper["value_unit_mapper"].get(record.value_unit, ""),
                    ]
                )

        return response
