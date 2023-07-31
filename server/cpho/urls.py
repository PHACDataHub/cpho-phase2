from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt

from graphene_django.views import GraphQLView

from cpho.schema import schema

from . import views

urlpatterns = [
    path(
        "graphql",
        csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema)),
    ),
    path(
        "indicators/", views.ListIndicators.as_view(), name="list_indicators"
    ),
    path(
        "indicators/<int:pk>/",
        views.ViewIndicator.as_view(),
        name="view_indicator",
    ),
    path(
        "indicators/<int:pk>/<int:period_pk>/",
        views.ViewIndicatorForPeriod.as_view(),
        name="view_indicator_for_period",
    ),
    path(
        "indicators/<int:pk>/edit/",
        views.EditIndicator.as_view(),
        name="edit_indicator",
    ),
    path(
        "indicators/create/",
        views.CreateIndicator.as_view(),
        name="create_indicator",
    ),
    path(
        "indicators/upload/",
        views.UploadIndicator.as_view(),
        name="upload_indicator",
    ),
    path(
        "indicators/<int:indicator_id>/period/<int:period_pk>/manage_data/<int:dimension_type_id>/",
        views.ManageIndicatorData.as_view(),
        name="manage_indicator_data",
    ),
    path(
        "indicators/<int:indicator_id>/period/<int:period_pk>/manage_data/all/",
        views.ManageIndicatorData.as_view(),
        name="manage_indicator_data_all",
    ),
    path(
        "indicators/<int:indicator_id>/period/<int:period_pk>/submit_data/<int:dimension_type_id>/",
        views.SubmitIndicatorData.as_view(),
        name="submit_indicator_data",
    ),
    path(
        "indicators/<int:indicator_id>/period/<int:period_pk>/submit_data/all/",
        views.SubmitIndicatorData.as_view(),
        name="submit_indicator_data_all",
    ),
    path(
        "indicators/<int:indicator_id>/period/<int:period_pk>/review_data/<int:dimension_type_id>/",
        views.ReviewData.as_view(),
        name="review_indicator_data",
    ),
    path(
        "indicators/<int:indicator_id>/period/<int:period_pk>/review_data/all/",
        views.ReviewData.as_view(),
        name="review_indicator_data_all",
    ),
    path(
        "global-changelog/",
        views.GlobalChangelog.as_view(),
        name="global_changelog",
    ),
    path(
        "global-changelog/<int:page_num>/",
        views.GlobalChangelog.as_view(),
        name="global_changelog",
    ),
]
