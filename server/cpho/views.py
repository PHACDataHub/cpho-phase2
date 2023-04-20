import csv
import json
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template import loader
from .models import IndicatorData, Indicator 
from io import TextIOWrapper

def index(request):
    return render(request, "index.html")