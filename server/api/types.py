# module expected to grow...

from django.db import models

import graphene
from graphene import List, NonNull
from graphene_django import DjangoObjectType
from rest_framework import serializers

from cpho.models import DimensionType as DimensionTypeModel
from cpho.models import DimensionValue as DimensionValueModel
from cpho.models import Indicator as IndicatorModel
from cpho.models import IndicatorDatum as IndicatorDatumModel
from cpho.models import Period as PeriodModel

from .dataloaders import (
    DimensionTypeByIdLoader,
    DimensionValueByIdLoader,
    IndicatorByIdLoader,
    PeriodByIdLoader,
    SubmittedDatumByIndicatorLoader,
    SubmittedDatumByIndicatorYearLoader,
    SubmittedPeriodsByIndicatorLoader,
)


class Indicator(DjangoObjectType):
    class Meta:
        model = IndicatorModel

    data = graphene.Field(
        NonNull(List(NonNull("api.types.IndicatorDatum"))),
        year=graphene.Argument(graphene.Int),
    )

    submitted_periods = graphene.Field(
        NonNull(List(NonNull("api.types.Period")))
    )

    def resolve_data(self, info, year=None):
        if year:
            return SubmittedDatumByIndicatorYearLoader(
                info.context.dataloaders
            ).load((self.id, year))
        else:
            return SubmittedDatumByIndicatorLoader(
                info.context.dataloaders
            ).load(self.id)

    def resolve_submitted_periods(self, info):
        return SubmittedPeriodsByIndicatorLoader(
            info.context.dataloaders
        ).load(self.id)


class IndicatorDatum(graphene.ObjectType):
    """
    Represents a submitted datum for an indicator
    """

    value = graphene.Float()
    literal_dimension_val = graphene.String()
    data_quality = graphene.String()
    reason_for_null = graphene.String()
    value_unit = graphene.String()
    value_displayed = graphene.String()
    single_year_timeframe = graphene.String()
    multiple_year_timeframe = graphene.String()

    period = graphene.Field(NonNull("api.types.Period"))

    def resolve_period(self, info):
        return PeriodByIdLoader(info.context.dataloaders).load(self.period_id)

    dimension_type = graphene.Field(NonNull("api.types.DimensionType"))

    def resolve_dimension_type(self, info):
        return DimensionTypeByIdLoader(info.context.dataloaders).load(
            self.dimension_type_id
        )

    dimension_value = graphene.Field("api.types.DimensionValue")

    def resolve_dimension_value(self, info):
        if not self.dimension_value_id:
            return None
        return DimensionValueByIdLoader(info.context.dataloaders).load(
            self.dimension_value_id
        )

    indicator = graphene.Field(NonNull("api.types.Indicator"))

    def resolve_indicator(self, info):
        return IndicatorByIdLoader(info.context.dataloaders).load(
            self.indicator_id
        )


class DimensionType(DjangoObjectType):
    class Meta:
        model = DimensionTypeModel


class DimensionValue(DjangoObjectType):
    class Meta:
        model = DimensionValueModel


class Period(DjangoObjectType):
    class Meta:
        model = PeriodModel
