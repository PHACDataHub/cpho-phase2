from cpho.schema import schema
from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

from . import views

app_name = "cpho"
urlpatterns = [
    path(
        "graphql",
        csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema)),
    ),
    path(
        "/indicators/", views.ListIndicators.as_view(), name="list_indicators"
    ),
    path(
        "/indicators/<int:pk>/",
        views.ViewIndicator.as_view(),
        name="view_indicator",
    ),
    path(
        "/indicators/<int:pk>/edit",
        views.EditIndicator.as_view(),
        name="edit_indicator",
    ),
    path(
        "/indicators/create/",
        views.CreateIndicator.as_view(),
        name="create_indicator",
    ),
]
