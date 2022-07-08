from django.db import models


class Indicator(models.Model):
    category = models.CharField(max_length=50)
    topic = models.CharField(max_length=50)
    indicator = models.CharField(max_length=50)
    detailed_indicator = models.CharField(max_length=300)
    sub_indicator_measurement = models.CharField(max_length=150)

    def __str__(self):
        return self.detailed_indicator


class IndicatorData(models.Model):
    indicator = models.ForeignKey(Indicator, on_delete=models.RESTRICT)
    country = models.CharField(max_length=50)
    geography = models.CharField(max_length=50)
    sex = models.CharField(max_length=50)
    gender = models.CharField(max_length=50)
    age_group = models.CharField(max_length=50)
    age_group_type = models.CharField(max_length=50)
    data_quality = models.CharField(max_length=50)
    value = models.FloatField()
    value_lower_bound = models.FloatField()
    value_upper_bound = models.FloatField()
    value_unit = models.CharField(max_length=50)
    single_year_timeframe = models.CharField(max_length=50)
    multi_year_timeframe = models.CharField(max_length=50)

    def __str__(self):
        return self.country+' '+self.sex+' '+self.age_group+' '+self.single_year_timeframe+self.multi_year_timeframe+' '+self.value


class Benchmarking(models.Model):
    indicator = models.ForeignKey(Indicator, on_delete=models.RESTRICT)
    detailed_indicator = models.CharField(max_length=150)
    value_unit = models.CharField(max_length=100)
    oced_country = models.CharField(max_length=100)
    value = models.FloatField(max_length=50)
    year = models.SmallIntegerField()
    standard_deviation = models.FloatField()
    comparison_to_oecd_avg = models.CharField(max_length=50)

    def __str__(self):
        return self.detailed_indicator


class TrendAnalysis(models.Model):
    indicator = models.ForeignKey(Indicator, on_delete=models.RESTRICT)
    detailed_indicator = models.CharField(max_length=250)
    year = models.SmallIntegerField()
    data_point = models.FloatField()
    line_of_best_fit_point = models.FloatField()

    def __str__(self):
        return self.detailed_indicator
