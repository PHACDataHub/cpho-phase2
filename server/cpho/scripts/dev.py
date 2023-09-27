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
    Period,
    PHACOrg,
    PhacOrgRole,
    User,
)
from cpho.util import GroupFetcher


@transaction.atomic
def run():
    create_users()
    create_data()


def create_users():
    # PhacOrgRole.objects.all().delete()
    # # create_phacorgs()
    User.objects.filter(username="admin").delete()
    admin = User.objects.create_superuser(
        username="admin",
        password="admin",
    )
    admin.groups.add(GroupFetcher.admin_group)
    User.objects.filter(username="person1").delete()
    User.objects.create_user(
        username="person1",
        password="person1",
    )
    User.objects.filter(username="hso").delete()
    hso = User.objects.create_user(
        username="hso",
        password="hso",
    )
    hso.groups.add(GroupFetcher.hso_group)
    branches = PHACOrg.branches()
    for branch in branches:
        branch_name = branch.acronym_en.lower().replace(" ", "")
        branch_lead = branch_name + "_lead"
        branch_user = branch_name + "_user"
        User.objects.filter(username=branch_lead).delete()
        created_lead = User.objects.create_user(
            username=branch_lead,
            password=branch_lead,
        )
        PhacOrgRole.objects.create(
            user=created_lead,
            phac_org=branch,
            is_phac_org_lead=True,
        )
        print("User created: ", branch_lead)

        User.objects.filter(username=branch_user).delete()
        created_user = User.objects.create_user(
            username=branch_user,
            password=branch_user,
        )
        PhacOrgRole.objects.create(
            user=created_user,
            phac_org=branch,
            is_phac_org_lead=False,
        )

        print("User created: ", branch_user)


def create_data():
    IndicatorDatum.objects.all().delete()
    Indicator.objects.all().delete()

    p2021 = Period.objects.get(year=2021, quarter=None, year_type="calendar")
    indicators = []
    users = User.objects.all()
    for user in users:
        if test_rule("is_branch_lead", user):
            for phac_org_role in user.phac_org_roles.all():
                phac_org = phac_org_role.phac_org
                for i in range(3):
                    indicator = IndicatorFactory(
                        PHACOrg=phac_org,
                    )
                    new_name = phac_org.acronym_en + " : " + indicator.name
                    if len(new_name) > 50:
                        new_name = new_name[:50]
                        new_name = new_name.rsplit(" ", maxsplit=1)[0]

                    indicator.name = new_name
                    indicator.save()
                    # indicator.relevant_dimensions.set(
                    #     DimensionType.objects.all()
                    # )
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
