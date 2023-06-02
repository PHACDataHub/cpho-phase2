from django.db import transaction

from cpho.model_factories import (
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
    User.objects.create_user(
        username="admin",
        password="admin",
    )

    User.objects.create_user(
        username="person1",
        password="person1",
    )


def create_data():
    p2021 = Period.objects.get(year=2021)
    indicators = IndicatorFactory.create_batch(10)
    for dimension in DimensionType.objects.all():
        for dimension_value in dimension.possible_values.all():
            for indicator in indicators:
                IndicatorDatumFactory(
                    indicator=indicator,
                    dimension_value=dimension_value,
                    period=p2021,
                )
