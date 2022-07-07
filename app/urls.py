from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('indicator', views.indicator, name='indicator'),
    path('pastsubmissions', views.pastsubmissions, name='pastsubmissions'),
    path('import', views.importPage, name='import'),
    path('export', views.exportPage, name='export'),
]