from django.urls import path
from graphene_django.views import GraphQLView
from cpho.schema import schema

from . import views

app_name = 'cpho'
urlpatterns = [
    path('', views.index, name='index'),
    path('api/import', views.importPage, name='import'),
    path('api/export', views.exportPage, name='export'),
    path("graphql", GraphQLView.as_view(graphiql=True, schema=schema)),
]
