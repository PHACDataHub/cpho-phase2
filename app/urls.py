from django.urls import path
from graphene_django.views import GraphQLView
from app.schema import schema

from . import views

app_name = 'app'
urlpatterns = [
    path('', views.index, name='index'),
    path('api/indicator/<int:indicator_id>',
         views.indicator, name='indicator'),
    path('api/pastsubmissions', views.pastSubmissions, name='pastsubmissions'),
    path('api/possibleindicators', views.possibleIndicators, name='possibleindicators'),
    path('api/addindicator', views.addIndicator, name='addindicator'),
    path('api/import', views.importPage, name='import'),
    path('api/export', views.exportPage, name='export'),
    path("graphql", GraphQLView.as_view(graphiql=True, schema=schema)),
]
