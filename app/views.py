import csv
import json
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template import loader
from .models import IndicatorData, Indicator
from io import TextIOWrapper

def index(request):
    return render(request, "index.html")


def indicator(request, indicator_id):
    categories = [
        {
            'id': 1,
            'label': 'Factors Influencing Health'
        },
        {
            'id': 2,
            'label': 'General Health Status'
        },
        {
            'id': 3,
            'label': 'Health Outcomes'
        },
    ]

    sub_categories = [
        {
            'id': 1,
            'label': 'Childhood and Family Risk and Protective Factors',
            'category': 1
        },
        {
            'id': 2,
            'label': 'Social Factors',
            'category': 1
        },
        {
            'id': 3,
            'label': 'Substance Use',
            'category': 1
        },
        {
            'id': 4,
            'label': 'Health Status',
            'category': 2
        },
        {
            'id': 5,
            'label': 'Chronic Diseases and Mental Health',
            'category': 3
        },
        {
            'id': 6,
            'label': 'Communicable Diseases',
            'category': 3
        }
    ]
    return JsonResponse({
        'indicator': indicator_id,
        'categories': categories,
        'sub_categories': sub_categories
    })

def addIndicator(request):
    return JsonResponse(request, safe=False)

def pastSubmissions(request):
    indicators = Indicator.objects.all().values()
    return JsonResponse(list(indicators), safe=False)

def importPage(request):
    print("===== Import Request")
    print(request.body)
    print(request.POST)
    print("GOT FILE")
    reader = csv.reader(TextIOWrapper(request.FILES['file'], encoding="utf8"), delimiter=',')
    print(reader)
    rowCount = 0
    for row in reader:
        if rowCount != 0:
            print("ROWWW")
            print(row)
            ind = Indicator.objects.update_or_create(
                category = row[0],
                topic = row[1],
                indicator = row[2],
                detailed_indicator = row[3],
                sub_indicator_measurement = row[4],
            )
            print(row[12])
            IndicatorData.objects.update_or_create(
                indicator = ind[0],
                country = row[5],
                geography = row[6],
                sex = row[7],
                gender = row[8],
                age_group = row[9],
                age_group_type = row[10],
                data_quality = row[11],
                value = row[12].replace('<', ''),
                value_lower_bound = row[13] if row[13] != 'NULL' else None,
                value_upper_bound = row[14] if row[14] != 'NULL' else None,
                value_unit = row[15],
                single_year_timeframe = row[16],
                multi_year_timeframe = row[17],
            )
        rowCount += 1
    print("DONE!!")
    return JsonResponse({'status': '200', 'message': 'Successly imported data!'})


def exportPage(request):
    return render(request, 'app/export.html')
