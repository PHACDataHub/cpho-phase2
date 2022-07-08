from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template import loader


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


def pastSubmissions(request):
    return render(request, 'app/pastsubmissions.html')


def importPage(request):
    return render(request, 'app/import.html')


def exportPage(request):
    return render(request, 'app/export.html')
