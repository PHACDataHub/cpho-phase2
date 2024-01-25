from django.db import transaction

from server.rules_framework import test_rule

from cpho.model_factories import (
    Indicator,
    IndicatorDatum,
    IndicatorDatumFactory,
    IndicatorFactory,
)
from cpho.models import (
    DimensionType,
    DimensionValue,
    IndicatorDirectory,
    Period,
    User,
)
from cpho.util import GroupFetcher


@transaction.atomic
def run():
    create_admins()
    create_data()


def create_admins():
    User.objects.filter(username="admin").delete()
    admin = User.objects.create_superuser(
        username="admin",
        password="admin",
    )
    admin.groups.add(GroupFetcher.admin_group)
    User.objects.filter(username="hso").delete()
    hso = User.objects.create_user(
        username="hso",
        password="hso",
    )
    hso.groups.add(GroupFetcher.hso_group)


NUM_DIRECTORIES = 4
NUM_INDICATORS_PER_DIR = 3
NUM_USERS_PER_DIR = 4


def create_data():
    User.objects.filter(username__startswith="person").delete()
    IndicatorDirectory.objects.all().delete()
    IndicatorDatum.objects.all().delete()
    Indicator.objects.all().delete()

    all_indicators = []
    for i in range(1, NUM_DIRECTORIES + 1):
        directory = IndicatorDirectory.objects.create(name=f"Directory {i}")
        for j in range(1, NUM_INDICATORS_PER_DIR + 1):
            ind = IndicatorFactory()
            all_indicators.append(ind)
            directory.indicators.add(ind)

        for k in range(1, NUM_USERS_PER_DIR + 1):
            username = f"person{i}_{k}"
            user = User.objects.create_user(
                username=username, password=username
            )
            directory.users.add(user)

    p2021 = Period.objects.get(year=2021, quarter=None, year_type="calendar")
    for dimension in DimensionType.objects.all():
        if not dimension.is_literal:
            for dimension_value in dimension.possible_values.all():
                for indicator in all_indicators:
                    IndicatorDatumFactory(
                        indicator=indicator,
                        dimension_value=dimension_value,
                        period=p2021,
                        dimension_type=dimension,
                    )
        else:
            for i in range(1):
                for indicator in all_indicators:
                    IndicatorDatumFactory(
                        indicator=indicator,
                        period=p2021,
                        dimension_type=dimension,
                    )
