import random

import factory

from cpho.models import (
    DimensionType,
    DimensionValue,
    Indicator,
    IndicatorDatum,
    Period,
)
from cpho.util import dropdown_mapper


class DimensionTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DimensionType

    name_en = factory.Faker("bs")
    name_fr = factory.Faker("bs")
    code = factory.Faker("bs")


class DimensionValueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DimensionValue

    dimension_type = factory.SubFactory(DimensionTypeFactory)
    name_en = factory.Faker("bs")
    name_fr = factory.Faker("bs")
    value = factory.Faker("bs")


class PeriodFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Period

    year = factory.Faker("year")
    name_en = factory.Faker("bs")
    name_fr = factory.Faker("bs")


class IndicatorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Indicator

    name = factory.Faker("bs")
    category = factory.LazyFunction(
        lambda: random.choice(
            [p for p in dropdown_mapper()["indicator_category"]]
        )
    )
    sub_category = factory.LazyFunction(
        lambda: random.choice(
            [p for p in dropdown_mapper()["indicator_sub_category"]]
        )
    )
    detailed_indicator = factory.Faker("bs")
    sub_indicator_measurement = factory.Faker("bs")


class IndicatorDatumFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = IndicatorDatum

    indicator = factory.SubFactory(IndicatorFactory)
    period = factory.SubFactory(PeriodFactory)
    dimension_value = factory.SubFactory(DimensionValueFactory)
    value = factory.Faker("pyfloat")
    data_quality = factory.LazyFunction(
        lambda: random.choice(
            [p for p in dropdown_mapper()["indicator_data_data_quality"]]
        )
    )
    value_unit = factory.LazyFunction(
        lambda: random.choice(
            [p for p in dropdown_mapper()["indicator_data_value_unit"]]
        )
    )
    value_lower_bound = factory.Faker("pyfloat")
    value_upper_bound = factory.Faker("pyfloat")
