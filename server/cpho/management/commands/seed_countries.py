from csv import DictReader
from pathlib import Path

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction

from cpho.models import Benchmarking, Country

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Command(BaseCommand):
    """Seeds the HOPIC database with Country from CSV"""

    help = "Seeds the HOPIC database with County from CSV"

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
            # Confirmation prompt
            if not kwargs["yes"] and kwargs["mode"] in ["reset", "wipe"]:
                confirm = input(
                    "This will delete all existing countries. Are you sure? (y/N) "
                )
                if confirm.lower() != "y":
                    print("Aborting...")
                    return

            # Create / update countries
            seed_countries(kwargs["mode"])


def seed_countries(mode):
    """Seed programs based on options (upsert, reset, insert_ignore)"""
    # TODO: Currently only supports "reset" and wipe
    if mode in ["reset", "wipe"]:
        # truncate Benchmarking before truncating Country
        Benchmarking.objects.all().delete()
        Country.objects.all().delete()
        if mode == "wipe":
            return
    create_countries(mode)


def create_countries(mode="reset"):
    updated_count = 0
    inserted_count = 0
    skipped_count = 0
    with open(BASE_DIR / "scripts/countries.csv", encoding="utf-8") as f:
        reader = DictReader(f)
        for data in reader:
            # TODO: remove this if statement
            if data["id"] != "":
                data["id"] = data["id"] if data["id"] != "" else None
                data["name_en"] = (
                    data["name_en"] if data["name_en"] != "" else None
                )
                data["name_fr"] = (
                    data["name_fr"] if data["name_fr"] != "" else None
                )

                if mode in ["insert_ignore", "upsert"]:
                    try:
                        country = Country.objects.get(id=data["id"])
                    except Country.DoesNotExist:
                        country = None

                    if country:
                        if mode == "upsert":
                            # Update existing Countries
                            country.name_en = data["name_en"]
                            country.name_fr = data["name_fr"]
                            country.save()
                            updated_count += 1
                        else:
                            skipped_count += 1
                        continue

                Country.objects.create(
                    id=data["id"],
                    name_en=data["name_en"],
                    name_fr=data["name_fr"],
                )
                inserted_count += 1

    if inserted_count > 0:
        print(f"Countries inserted: {inserted_count}")
    if updated_count > 0:
        print(f"Countries updated: {updated_count}")
    if skipped_count > 0:
        print(f"Countries skipped: {skipped_count}")
