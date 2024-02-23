import csv

from django.http import HttpResponse
from django.utils.functional import cached_property
from django.views.generic import View

from phac_aspc.rules import test_rule

from cpho.models import Benchmarking, Indicator
from cpho.views.view_util import metadata_mapper

from .view_util import MustPassAuthCheckMixin


class ExportBenchmarking(MustPassAuthCheckMixin, View):
    def check_rule(self):
        return test_rule(
            "can_export_benchmarking",
            self.request.user,
            self.indicator,
        )

    @cached_property
    def indicator(self):
        if "indicator_id" in self.kwargs:
            return Indicator.objects.get(pk=self.kwargs["indicator_id"])
        else:
            return None

    def get(self, request, *args, **kwargs):
        benchmarking_data_qs = Benchmarking.active_objects.filter(
            indicator=self.indicator
        )

        filename = "benchmarking_template"
        if self.indicator:
            # remove commas to avoid issues with csv
            filename = (
                str(self.indicator.name).replace(",", "") + "_benchmarking"
            )

        response = HttpResponse(
            content_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}.csv"
            },
        )

        writer = csv.writer(response)
        header_row = [
            "Indicator_Trend",
            "Detailed_Indicator_Trend",
            "Unit",
            "OECD_Country",
            "Value",
            "Year",
            # "Standard_Deviation",
            "Comparison_to_OECD_average",
            "Labels (multiple graphs only)",
        ]
        writer.writerow(header_row)

        if benchmarking_data_qs:
            # mapper = metadata_mapper()
            for benchmarking_data in benchmarking_data_qs:
                data_row = [
                    benchmarking_data.indicator.name,
                    benchmarking_data.indicator.detailed_indicator,
                    benchmarking_data.unit,
                    benchmarking_data.oecd_country,
                    benchmarking_data.value,
                    benchmarking_data.year,
                    # benchmarking_data.standard_deviation,
                    benchmarking_data.comparison_to_oecd_avg,
                    benchmarking_data.labels,
                ]
                writer.writerow(data_row)
        return response
