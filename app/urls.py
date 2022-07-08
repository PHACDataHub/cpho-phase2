from django.urls import path

from . import views

app_name = 'app'
urlpatterns = [
    path('', views.index, name='index'),
    path('api/indicator/<int:indicator_id>',
         views.indicator, name='indicator'),
    path('api/pastsubmissions', views.pastSubmissions, name='pastsubmissions'),
    path('api/import', views.importPage, name='import'),
    path('api/export', views.exportPage, name='export'),
]
