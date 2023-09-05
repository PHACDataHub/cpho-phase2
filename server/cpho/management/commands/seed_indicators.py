from django.core.management.base import BaseCommand
from django.db import transaction

from server.rules_framework import test_rule

from cpho.model_factories import (
    Indicator,
    IndicatorDatum,
    IndicatorDatumFactory,
    IndicatorFactory,
)
from cpho.models import DimensionType, Period, User


class Command(BaseCommand):
    """Seeds the HOPIC database with fake indicators and indicator datum"""

    help = "Seeds the HOPIC database with fake indicators and indicator datum"

    def add_arguments(self, parser):
        parser.add_argument(
            "--num_indicators",
            type=int,
            default=5,
            help="number of fake indicators per branch_lead to create",
        )

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            create_data(kwargs["num_indicators"])


def create_data(num_indicators):
    IndicatorDatum.objects.all().delete()
    Indicator.objects.all().delete()

    p2021 = Period.objects.get(year=2021, quarter=None, year_type="calendar")
    indicators = []
    users = User.objects.all()
    for user in users:
        if test_rule("is_branch_lead", user):
            for phac_org_role in user.phac_org_roles.all():
                phac_org = phac_org_role.phac_org
                for i in range(num_indicators):
                    indicator = IndicatorFactory(
                        PHACOrg=phac_org,
                    )
                    new_name = phac_org.acronym_en + " : " + indicator.name
                    if len(new_name) > 50:
                        new_name = new_name[:50]
                        new_name = new_name.rsplit(" ", maxsplit=1)[0]

                    indicator.name = new_name
                    indicator.save()
                    indicators.append(indicator)

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
