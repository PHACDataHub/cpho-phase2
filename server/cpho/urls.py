from django.urls import path, re_path
from cpho.schema import schema
from django.views.decorators.csrf import csrf_exempt
from graphene_file_upload.django import FileUploadGraphQLView

from . import views

app_name = 'cpho'
urlpatterns = [
    path("graphql", csrf_exempt(FileUploadGraphQLView.as_view(graphiql=True, schema=schema)))
]
