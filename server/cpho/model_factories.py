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


class IndicatorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Indicator

    name = factory.Faker("bs")
    category = factory.LazyFunction(
        lambda: random.choice([p[0] for p in Indicator.CATEGORY_CHOICES])
    )
    topic = factory.LazyFunction(
        lambda: random.choice([p[0] for p in Indicator.TOPIC_CHOICES])
    )
    detailed_indicator = factory.Faker("bs")
    sub_indicator_measurement = factory.Faker("bs")

    @factory.post_generation
    def relevant_dimensions(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for dimension in extracted:
                self.relevant_dimensions.add(dimension)
            return
        self.relevant_dimensions.set(DimensionType.objects.all())


class IndicatorDatumFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = IndicatorDatum

    indicator = factory.SubFactory(IndicatorFactory)
    period = factory.Iterator(Period.objects.all())
    dimension_type = factory.SubFactory(DimensionTypeFactory)
    dimension_value = factory.Maybe(
        "dimension_type.is_literal",
        yes_declaration=None,
        no_declaration=factory.SubFactory(DimensionValueFactory),
    )

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
    literal_dimension_val = factory.LazyAttribute(
        lambda o: "custom value" if o.dimension_type.is_literal else None
    )
    value_lower_bound = factory.Faker(
        "pyfloat", positive=True, min_value=1, max_value=20
    )
    value_upper_bound = factory.Faker(
        "pyfloat", positive=True, min_value=80, max_value=100
    )
    value = factory.Faker(
        "pyfloat",
        positive=True,
        min_value=21,
        max_value=79,
    )
