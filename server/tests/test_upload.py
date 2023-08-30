import io

from django.urls import reverse

from cpho.models import DimensionType, Indicator, IndicatorDatum, Period

from .utils_for_tests import patch_rules


def test_import(hso_client):
    data = {}
    data["csv_file"] = io.BytesIO(
        b'Indicator,Detailed Indicator,Sub_Indicator_Measurement,Category,Topic,Data_Quality,Value,Value_LowerCI,Value_UpperCI,SingleYear_TimeFrame,MultiYear_TimeFrame,Value_Displayed,Dimension_Type,Dimension_Value,Period\r\nTest Upload,synergize mission-critical content,re-contextualize value-added action-items,HEALTH OUTCOMES,SUBSTANCE USE,CAUTION,39.882262018304,15.2404,93.85413575209,,,"PER 100,000",Sex,MALES,FY2023\r\nTest Upload,synergize mission-critical content,re-contextualize value-added action-items,HEALTH OUTCOMES,SUBSTANCE USE,SUPPRESSED,52.4,12.3550187,82.78,,,"PER 100,000 LIVE BIRTHS",Sex,FEMALES,FY2023\r\n'
    )
    data["csv_file"].name = "test.csv"
    url = reverse("upload_indicator")
    with patch_rules(can_upload_indicator=True):
        response = hso_client.post(
            url,
            data=data,
            # follow_redirects=True,
            # content_type="multipart/form-data",
        )
    assert response.status_code == 302
    assert response["Content-Type"] == "text/html; charset=utf-8"

    indicator = Indicator.objects.get(name="Test Upload")
    assert indicator.name == "Test Upload"
    assert len(IndicatorDatum.objects.filter(indicator=indicator)) == 2
