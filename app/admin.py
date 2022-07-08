from django.contrib import admin

from .models import Indicator, Benchmarking, IndicatorData, TrendAnalysis

admin.site.register([Indicator, Benchmarking, TrendAnalysis, IndicatorData])
