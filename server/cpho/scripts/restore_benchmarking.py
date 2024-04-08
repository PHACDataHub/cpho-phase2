from csv import DictReader
from pathlib import Path

from django.db import transaction

from cpho.models import Benchmarking, Country, Indicator


@transaction.atomic
def run():
    with open(
        Path(__file__).resolve().parent / "Benchmarking_2024.04.04.csv",
        encoding="utf-8-sig",
    ) as f:
        reader = DictReader(f)
        data = list(reader)

        rows_inserted = 0

        for row in data:

            print(row)

            if row["Indicator_Trend"] in [
                "OPIOID TOXICITY DEATHS",
                "DIABETES",
            ]:
                continue
            indicator = get_indicator(
                row["Indicator_Trend"], row["Detailed_Indicator_Trend"]
            )
            country = get_country(row["OECD_Country"])
            labels = row["Labels (multiple graphs only)"].lower()
            if labels not in [item[0] for item in Benchmarking.LABEL_CHOICES]:
                raise ValueError(f"Invalid label: {labels}")

            comparison = row["Comparison_to_OECD_average"].lower()
            if comparison not in [
                item[0] for item in Benchmarking.COMPARISON_CHOICES
            ]:
                raise ValueError(f"Invalid comparison: {comparison}")

            unit = row["Unit"].lower() if row["Unit"] != "--" else ""
            if unit not in [item[0] for item in Benchmarking.UNIT_CHOICES]:
                raise ValueError(f"Invalid unit: {unit}")

            year = int(row["Year"]) if row["Year"] != "--" else None

            # # check if already exists
            # query = Benchmarking.objects.filter(
            #     indicator=Indicator,
            #     oecd_country=Country,
            #     is_deleted=False,
            #     labels=labels,
            # )

            # if len(query) == 0:
            #     Benchmarking.objects.create(
            #         indicator=Indicator,
            #         oecd_country=Country,
            #         year=row["Year"],
            #         value=row["Value"],
            #     )
            #     rows_inserted += 1


def get_indicator(Indicator_Trend, Detailed_Indicator_Trend):
    qs = Indicator.objects.filter(
        name=Indicator_Trend, detailed_indicator=Detailed_Indicator_Trend
    )
    if len(qs) == 1:
        return qs[0]
    else:
        print(Indicator_Trend, Detailed_Indicator_Trend)
        print(qs)
        raise ValueError(
            f"More or less than one indicator found for: {Indicator_Trend}, {Detailed_Indicator_Trend}"
        )


def get_country(country):
    if country == "OECD Average":
        country = "OECD"
    qs = Country.objects.filter(name_en=country)
    if len(qs) == 1:
        return qs[0]
    else:
        print(country)
        print(qs)
        raise ValueError(f"More or less than one country found for: {country}")
