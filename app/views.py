import csv
import json
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template import loader
from .models import IndicatorData, Indicator 
from io import TextIOWrapper

def index(request):
    return render(request, "index.html")

def importPage(request):
    print("===== Import Request")
    print(request.body)
    print(request.POST)
    print("GOT FILE")
    reader = csv.reader(TextIOWrapper(request.FILES['file'], encoding="utf8"), delimiter=',')
    print(reader)
    rowCount = 0
    for row in reader:
        if rowCount != 0 and row != []:
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
                value_lower_bound = row[13] if row[13] != '' else None,
                value_upper_bound = row[14] if row[14] != '' else None,
                value_unit = row[15],
                single_year_timeframe = row[16],
                multi_year_timeframe = row[17],
            )
        rowCount += 1
    print("DONE!!")
    return JsonResponse({'status': '200', 'message': 'Successly imported data!'})

def exportPage(request):
    indicator_ids = json.loads(request.POST.get('selectedIndicators'))

    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="results.csv"'},
    )

    fieldnames = ['category', 'topic', 'indicator', 'detailed_indicator', 'sub_indicator_measurement', 'country', 'geography', 'sex', 'gender', 'age_group', 'age_group_type', 'data_quality', 'value', 'value_lower_bound', 'value_upper_bound', 'value_unit', 'single_year_timeframe', 'multi_year_timeframe']
    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()

    for id in indicator_ids:
            ind = Indicator.objects.get(id=id)
            points = IndicatorData.objects.all().filter(indicator=ind.id)
            for point in points:
                writer.writerow({
                    'category': ind.category,
                    'topic': ind.topic,
                    'indicator': ind.indicator,
                    'detailed_indicator': ind.detailed_indicator,
                    'sub_indicator_measurement': ind.sub_indicator_measurement,
                    'country': point.country,
                    'geography': point.geography,
                    'sex': point.sex,
                    'gender': point.gender,
                    'age_group': point.age_group,
                    'age_group_type': point.age_group_type,
                    'data_quality': point.data_quality,
                    'value': point.value,
                    'value_lower_bound': point.value_lower_bound,
                    'value_upper_bound': point.value_upper_bound,
                    'value_unit': point.value_unit,
                    'single_year_timeframe': point.single_year_timeframe,
                    'multi_year_timeframe': point.multi_year_timeframe
                })
    return response
