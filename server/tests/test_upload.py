import io

from django.urls import reverse

from phac_aspc.rules import patch_rules

from cpho.models import DimensionType, Indicator, IndicatorDatum, Period


def test_import(hso_client):
    data = {}
    # byte file mimicking a file with the following contents:
    # indicator name = Test Upload
    # 2 data points
    data["csv_file"] = io.BytesIO(
        b'Category,Topic,Indicator,Detailed Indicator,Sub_Indicator_Measurement,Data_Quality,Value,Value_LowerCI,Value_UpperCI,Value_Displayed,SingleYear_TimeFrame,MultiYear_TimeFrame,Dimension_Type,Dimension_Value,Period,Reason_for_Null_Data,Value_Units,Arrow_Flag\r\nFACTORS INFLUENCING HEALTH,SOCIAL FACTORS,Test Upload,strategize e-business supply-chains,revolutionize cross-media e-business,ACCEPTABLE,58.98178803,5.65398,83.99,%,,,Sex,MALES,CY2022,Suppressed,PERCENTAGE (CRUDE),UP\r\nFACTORS INFLUENCING HEALTH,SOCIAL FACTORS,Test Upload,strategize e-business supply-chains,revolutionize cross-media e-business,,60.611,6.78,95.178702,%,,,Sex,FEMALES,CY2022,Not available,"RATE PER 100,000 POPULATION PER YEAR",DOWN\r\n'
    )
    data["csv_file"].name = "test.csv"
    url = reverse("upload_indicator")
    with patch_rules(can_use_indicator_upload=True):
        response = hso_client.post(
            url,
            data=data,
        )
    assert response.status_code == 302
    assert response["Content-Type"] == "text/html; charset=utf-8"

    url = reverse("save_upload")
    with patch_rules(can_use_indicator_upload=True):
        response = hso_client.post(
            url,
        )
    assert response.status_code == 200

    indicator = Indicator.objects.get(name="Test Upload")
    assert indicator.name == "Test Upload"
    assert len(IndicatorDatum.active_objects.filter(indicator=indicator)) == 2
