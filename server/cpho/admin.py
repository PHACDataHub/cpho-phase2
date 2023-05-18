from django.contrib import admin

from .models import Benchmarking, Indicator, IndicatorData, TrendAnalysis

admin.site.register([Indicator, Benchmarking, TrendAnalysis, IndicatorData])
