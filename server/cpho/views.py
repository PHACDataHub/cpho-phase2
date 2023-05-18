import csv
import json
from io import TextIOWrapper

from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template import loader

from .models import Indicator, IndicatorData


def index(request):
    return render(request, "index.html")
