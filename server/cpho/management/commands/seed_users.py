from django.core.management.base import BaseCommand
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


class Command(BaseCommand):
    help = "Seeds the HOPIC database with Admin, program-lead and program-user user accounts"

    def add_arguments(self, parser):
        parser.add_argument(
            "--program_lead",
            type=bool,
            default=True,
            help="Create program lead users",
        )
        parser.add_argument(
            "--program_user",
            type=bool,
            default=True,
            help="Create program user users",
        )

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            create_users(kwargs["program_lead"], kwargs["program_user"])


def create_users(program_lead, program_user):
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

    if program_lead or program_user:
        branches = PHACOrg.branches()
        for branch in branches:
            branch_name = branch.acronym_en.lower().replace(" ", "")
            branch_lead = branch_name + "_lead"

            if program_lead:
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

            if program_user:
                branch_user = branch_name + "_user"
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
