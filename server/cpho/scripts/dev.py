from csv import DictReader
from pathlib import Path

from django.db import transaction

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

BASE_DIR = Path(__file__).resolve().parent


@transaction.atomic
def run():
    create_users()
    create_data()
    create_phacorgs()


def create_users():
    User.objects.filter(username="admin").delete()
    User.objects.create_superuser(
        username="admin",
        password="admin",
    )
    User.objects.filter(username="person1").delete()
    User.objects.create_user(
        username="person1",
        password="person1",
    )
    User.objects.filter(username="hso").delete()
    User.objects.create_user(
        username="hso",
        password="hso",
    )
    User.objects.filter(username="program").delete()
    User.objects.create_user(
        username="program",
        password="program",
    )


def create_phacorgs(mode="reset"):
    if mode == "reset":
        PhacOrgRole.objects.all().delete()
        PHACOrg.objects.all().delete()
    updated_count = 0
    inserted_count = 0
    skipped_count = 0
    with open(BASE_DIR / "phac_orgs.csv", encoding="utf-8") as f:
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


def create_data():
    IndicatorDatum.objects.all().delete()
    Indicator.objects.all().delete()

    p2021 = Period.objects.get(year=2021, quarter=None, year_type="calendar")
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
