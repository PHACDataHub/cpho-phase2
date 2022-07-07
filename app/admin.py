from django.contrib import admin

from .models import Indicator, Benchmarking, TrendAnalysis

admin.site.register([Indicator, Benchmarking, TrendAnalysis])