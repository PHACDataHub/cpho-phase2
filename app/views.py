from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.template import loader

def index(request):
    return render(request, 'app/index.html')

def indicator(request):
    return render(request, 'app/indicator.html')

def pastsubmissions(request):
    return render(request, 'app/pastsubmissions.html')

def importPage(request):
    return render(request, 'app/import.html')

def exportPage(request):
    return render(request, 'app/export.html')