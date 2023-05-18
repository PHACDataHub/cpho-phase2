from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt

from graphene_django.views import GraphQLView

from cpho.schema import schema

from . import views

app_name = "cpho"
urlpatterns = [
    path(
        "graphql",
        csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema)),
    )
]
