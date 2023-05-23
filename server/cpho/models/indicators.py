from django.db import models

from server import fields
from server.model_util import (add_to_admin, track_versions_with_editor,
                               track_versions_with_editor_and_approval)


@add_to_admin
@track_versions_with_editor
class Indicator(models.Model):
    name = fields.CharField(max_length=50)

    category = fields.CharField(max_length=50)

    sub_category = fields.CharField(max_length=50)

    detailed_indicator = fields.CharField(max_length=300)

    sub_indicator_measurement = fields.CharField(max_length=150)

    def __str__(self):
        return self.detailed_indicator


@add_to_admin
@track_versions_with_editor_and_approval
class IndicatorDatum(models.Model):
    indicator = fields.ForeignKey(Indicator, null=False, on_delete=models.RESTRICT)

    dimension_value = fields.ForeignKey("cpho.DimensionValue", null=False, blank=False, on_delete=models.RESTRICT)

    period = fields.ForeignKey("cpho.Period", null=True, blank=True, on_delete=models.RESTRICT)

    data_quality = fields.CharField(max_length=50)

    value = fields.FloatField()

    value_lower_bound = fields.FloatField(null=True)

    value_upper_bound = fields.FloatField(null=True)

    value_unit = fields.CharField(max_length=50)

    single_year_timeframe = fields.CharField(max_length=50, null=True)

    multi_year_timeframe = fields.CharField(max_length=50, null=True)

    def __str__(self):
        return " ".join(
            [
                self.location_type,
                self.location,
                str(self.value),
            ]
        )


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
