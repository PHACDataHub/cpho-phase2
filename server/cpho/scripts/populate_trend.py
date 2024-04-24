from csv import DictReader
from pathlib import Path

from django.db import transaction

from cpho.models import Country, Indicator, TrendAnalysis


@transaction.atomic
def run():
    with open(
        Path(__file__).resolve().parent / "Trend_data.csv",
        encoding="utf-8-sig",
    ) as f:
        reader = DictReader(f)
        data = list(reader)

        rows_inserted = 0

        for row in data:

            print(row)

            indicator = get_indicator(
                row["Indicator_Trend"], row["Detailed_Indicator_Trend"]
            )

            trend = row["Trend"].lower()
            if trend not in [item[0] for item in TrendAnalysis.TREND_CHOICES]:
                raise ValueError(f"Invalid trend: {trend}")

            data_quality = (
                row["Data quality"].lower().strip().replace(" ", "_")
            )
            if data_quality not in [
                item[0] for item in TrendAnalysis.DATA_QUALITY_CHOICES
            ]:
                raise ValueError(f"Invalid data quality: {data_quality}")

            unit = row["Unit"].lower() if row["Unit"] != "--" else ""
            if unit not in [item[0] for item in TrendAnalysis.UNIT_CHOICES]:
                raise ValueError(f"Invalid unit: {unit}")

            year = row["Single Year / Year Range"].strip()

            trend_segment = row["Trend segment"].strip()

            data_point = None
            try:
                data_point = float(row["Data point"])
            except ValueError:
                pass

            line_of_bf = None
            try:
                line_of_bf = float(row["Line of best fit point"])
            except ValueError:
                pass

            data_upper = None
            try:
                data_upper = float(row["Data upper CI"])
            except ValueError:
                pass

            data_lower = None
            try:
                data_lower = float(row["Data lower CI"])
            except ValueError:
                pass

            # check if already exists
            query = TrendAnalysis.objects.filter(
                indicator=indicator,
                year=year,
                is_deleted=False,
            )

            if len(query) == 0:
                TrendAnalysis.objects.create(
                    indicator=indicator,
                    year=year,
                    data_point=data_point,
                    line_of_best_fit_point=line_of_bf,
                    trend_segment=trend_segment,
                    trend=trend,
                    data_quality=data_quality,
                    unit=unit,
                    data_point_upper_ci=data_upper,
                    data_point_lower_ci=data_lower,
                )
                rows_inserted += 1
            else:
                duplicate = None
                for obj in query:
                    if (
                        obj.data_point == data_point
                        and obj.line_of_best_fit_point == line_of_bf
                        and obj.trend_segment == trend_segment
                        and obj.trend == trend
                        and obj.data_quality == data_quality
                        and obj.unit == unit
                        and obj.data_point_upper_ci == data_upper
                        and obj.data_point_lower_ci == data_lower
                    ):
                        duplicate = True
                        break
                if duplicate:
                    print("Duplicate found")
                    continue

                raise ValueError(
                    f"More than one trend found for: {indicator}, {year}"
                )


def get_indicator(Indicator_Trend, Detailed_Indicator_Trend):
    qs = Indicator.objects.filter(
        name=Indicator_Trend,
    )
    if len(qs) > 1:
        qs = qs.filter(detailed_name=Detailed_Indicator_Trend)

    if Indicator_Trend == "OPIOID TOXICITY DEATHS":
        qs = qs.filter(
            sub_indicator_measurement="Rate of apparent opioid toxicity deaths per 100,000"
        )
    if len(qs) == 1:
        return qs[0]
    else:

        print(Indicator_Trend, Detailed_Indicator_Trend)
        print(qs)
        raise ValueError(
            f"More or less than one indicator found for: {Indicator_Trend}, {Detailed_Indicator_Trend}"
        )
