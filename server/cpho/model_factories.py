import random

import factory

from cpho.models import (
    DimensionType,
    DimensionValue,
    Indicator,
    IndicatorDatum,
    Period,
)


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
        lambda: random.choice([p[0] for p in Indicator.CATEGORY_CHOICES])
    )
    sub_category = factory.LazyFunction(
        lambda: random.choice([p[0] for p in Indicator.SUB_CATEGORY_CHOICES])
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
            [p[0] for p in IndicatorDatum.DATA_QUALITY_CHOICES]
        )
    )
    value_unit = factory.LazyFunction(
        lambda: random.choice(
            [p[0] for p in IndicatorDatum.VALUE_UNIT_CHOICES]
        )
    )
    value_lower_bound = factory.Faker("pyfloat")
    value_upper_bound = factory.Faker("pyfloat")