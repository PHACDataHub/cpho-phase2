from django.db import transaction

from cpho.model_factories import (
    Indicator,
    IndicatorDatum,
    IndicatorDatumFactory,
    IndicatorFactory,
)
from cpho.models import DimensionType, DimensionValue, Period, User


@transaction.atomic
def run():
    create_users()
    create_data()


def create_users():
    User.objects.filter(username="admin").delete()
    User.objects.create_user(
        username="admin",
        password="admin",
    )
    User.objects.filter(username="person1").delete()
    User.objects.create_user(
        username="person1",
        password="person1",
    )


def create_data():
    IndicatorDatum.objects.all().delete()
    Indicator.objects.all().delete()

    p2021 = Period.objects.get(year=2021)
    indicators = IndicatorFactory.create_batch(10)
    for dimension in DimensionType.objects.all():
        if not dimension.is_literal:
            for dimension_value in dimension.possible_values.all():
                for indicator in indicators:
                    IndicatorDatumFactory(
                        indicator=indicator,
                        dimension_value=dimension_value,
                        period=p2021,
                        dimension_type=dimension,
                    )
        else:
            for i in range(1):
                for indicator in indicators:
                    IndicatorDatumFactory(
                        indicator=indicator,
                        period=p2021,
                        dimension_type=dimension,
                    )
