from django.urls import reverse

from phac_aspc.rules import patch_rules

from cpho.model_factories import IndicatorDatumFactory, IndicatorFactory
from cpho.models import Benchmarking, Country, TrendAnalysis


def test_infobase_export(vanilla_user_client):
    url = reverse("infobase_export")

    canada = Country.objects.get(name_en="Canada")

    indicators = IndicatorFactory.create_batch(5)
    for i in indicators:
        IndicatorDatumFactory.create_batch(5, indicator=i)

        Benchmarking.objects.create(
            indicator=i, oecd_country=canada, value=1, year=2020
        )
        TrendAnalysis.objects.create(
            indicator=i,
            data_point=1.1,
            year="2019-2020",
            trend=TrendAnalysis.TREND_CHOICES[1][0],
        )

    with patch_rules(is_admin_or_hso=False):
        response = vanilla_user_client.get(url)
        assert response.status_code == 403

    with patch_rules(is_admin_or_hso=True):
        response = vanilla_user_client.get(url)
        assert response.status_code == 200
        assert response["Content-Type"] == "application/vnd.ms-excel"
        assert response.content
