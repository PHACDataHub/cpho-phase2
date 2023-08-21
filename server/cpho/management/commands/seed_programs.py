from csv import DictReader
from pathlib import Path

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction

from cpho.models import (
    DimensionType,
    DimensionValue,
    Indicator,
    IndicatorDatum,
    Period,
    PHACOrg,
    PhacOrgRole,
    User,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Command(BaseCommand):
    """Seeds the HOPIC database with PHAC orgs from CSV and creates admin group"""

    help = "Seeds the HOPIC database with PHAC orgs from CSV and creates admin group"

    def add_arguments(self, parser):
        parser.add_argument(
            "--mode",
            type=str,
            default="upsert",
            help="Program seeding options: wipe, reset, upsert, insert_ignore. Default is upsert",
        )
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Automatically accepts all confirmation prompts (risky!). Default is False",
        )

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            # We always need admin / account admin groups! This is non-destructive
            # Group.objects.get_or_create(name=ITAP_ADMIN_GROUP)
            # Group.objects.get_or_create(name=ITAP_ACCOUNT_ADMIN_GROUP)

            # Confirmation prompt
            if not kwargs["yes"] and kwargs["mode"] in ["reset", "wipe"]:
                confirm = input(
                    "This will delete all existing PHAC orgs. Are you sure? (y/N) "
                )
                if confirm.lower() != "y":
                    print("Aborting...")
                    return

            # Create / update programs
            seed_programs(kwargs["mode"])


def seed_programs(mode):
    """Seed programs based on options (upsert, reset, insert_ignore)"""
    # TODO: Currently only supports "reset" and wipe
    if mode in ["reset", "wipe"]:
        IndicatorDatum.objects.all().delete()
        Indicator.objects.all().delete()
        # Remove existing programs
        PhacOrgRole.objects.all().delete()
        PHACOrg.objects.all().delete()
        print("PHAC orgs wiped")
        if mode == "wipe":
            return
    create_phacorgs(mode)


def create_phacorgs(mode="reset"):
    IndicatorDatum.objects.all().delete()
    Indicator.objects.all().delete()
    if mode == "reset":
        PhacOrgRole.objects.all().delete()
        PHACOrg.objects.all().delete()

    updated_count = 0
    inserted_count = 0
    skipped_count = 0
    with open(BASE_DIR / "scripts/phac_orgs.csv", encoding="utf-8") as f:
        reader = DictReader(f)
        for data in reader:
            data["pk"] = data["pk"] if data["pk"] != "" else None
            data["parent_pk"] = (
                data["parent_pk"] if data["parent_pk"] != "000000" else None
            )

            if mode in ["insert_ignore", "upsert"]:
                try:
                    phac_org = PHACOrg.objects.get(id=data["pk"])
                except PHACOrg.DoesNotExist:
                    phac_org = None

                if phac_org:
                    if mode == "upsert":
                        # Update existing PHACOrg
                        phac_org.name_en = data["name_en"]
                        phac_org.name_fr = data["name_fr"]
                        phac_org.acronym_fr = data["acronym_fr"]
                        phac_org.acronym_en = data["acronym_en"]
                        phac_org.parent_id = data["parent_pk"]
                        phac_org.save()
                        updated_count += 1
                    else:
                        skipped_count += 1
                    continue

            PHACOrg.objects.create(
                id=data["pk"],
                name_en=data["name_en"],
                name_fr=data["name_fr"],
                acronym_fr=data["acronym_fr"],
                acronym_en=data["acronym_en"],
                parent_id=data["parent_pk"] or None,
            )
            inserted_count += 1

    if inserted_count > 0:
        print(f"PHAC orgs inserted: {inserted_count}")
    if updated_count > 0:
        print(f"PHAC orgs updated: {updated_count}")
    if skipped_count > 0:
        print(f"PHAC orgs skipped: {skipped_count}")
