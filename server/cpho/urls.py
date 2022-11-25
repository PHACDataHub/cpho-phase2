from django.urls import path, re_path
from graphene_django.views import GraphQLView
from cpho.schema import schema

from . import views

app_name = 'cpho'
urlpatterns = [
    path('api/import', views.importPage, name='import'),
    path('api/export', views.exportPage, name='export'),
    re_path(r'.*', GraphQLView.as_view(graphiql=True, schema=schema)), # Catch all other urls to GraphQL API
]
