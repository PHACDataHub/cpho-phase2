import csv

from django.urls import reverse

from cpho.model_factories import IndicatorDatumFactory, IndicatorFactory
from cpho.models import DimensionType, Indicator, Period

from .utils_for_tests import patch_rules


def test_export(vanilla_user_client):
    indicator = IndicatorFactory(
        name="Test Indicator",
        category=Indicator.CATEGORY_CHOICES[-1][0],
    )
    sex_dim_type = DimensionType.objects.get(code="sex")
    period = Period.objects.last()
    possible_dimension_value = sex_dim_type.possible_values.all()
    datum_male = IndicatorDatumFactory(
        indicator=indicator,
        dimension_value=possible_dimension_value[0],
        period=period,
        dimension_type=sex_dim_type,
    )
    datum_male.save()
    datum_female = IndicatorDatumFactory(
        indicator=indicator,
        dimension_value=possible_dimension_value[1],
        period=period,
        dimension_type=sex_dim_type,
    )
    datum_female.save()

    url = reverse("export_indicator", kwargs={"pk": indicator.pk})
    with patch_rules(can_export_indicator=True):
        response = vanilla_user_client.get(url)
    assert response.status_code == 200
    assert response["Content-Disposition"] == (
        f"attachment; filename={indicator.name}.csv"
    )
    assert response["Content-Type"] == "text/csv"
    contents = response.content.decode("utf-8-sig").splitlines()
    reader = csv.DictReader(contents)

    for data in reader:
        if data["Dimension_Value"] == "MALES":
            datum = datum_male
        else:
            datum = datum_female

        assert data["Indicator"] == str(datum.indicator.name)
        assert data["Period"] == str(datum.period.code)
        assert data["Value"] == str(datum.value)
