import csv

from django.http import HttpResponse
from django.utils.functional import cached_property
from django.views.generic import View

from cpho.models import Indicator, IndicatorDatum
from cpho.views.view_util import export_mapper


class ExportIndicator(View):
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
            filename = indicator.name

        response = HttpResponse(
            content_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}.csv"
            },
        )

        writer = csv.writer(response)
        header_row = [
            "Indicator",
            "Detailed Indicator",
            "Sub_Indicator_Measurement",
            "Category",
            "Topic",
            "Data_Quality",
            "Value",
            "Value_LowerCI",
            "Value_UpperCI",
            "SingleYear_TimeFrame",
            "MultiYear_TimeFrame",
            "Value_Displayed",
            "Dimension_Type",
            "Dimension_Value",
            "Period",
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
                        indicator.name,
                        indicator.detailed_indicator,
                        indicator.sub_indicator_measurement,
                        mapper["category_mapper"].get(indicator.category, ""),
                        mapper["subcategory_mapper"].get(
                            indicator.sub_category, ""
                        ),
                        mapper["data_quality_mapper"].get(
                            record.data_quality, ""
                        ),
                        record.value,
                        record.value_lower_bound,
                        record.value_upper_bound,
                        record.single_year_timeframe,
                        record.multi_year_timeframe,
                        mapper["value_unit_mapper"].get(record.value_unit),
                        mapper["dimension_type_mapper"].get(
                            record.dimension_type, ""
                        ),
                        deduced_dimension_value,
                        record.period.generate_code,
                    ]
                )

        return response
