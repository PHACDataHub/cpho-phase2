import io

from django.urls import reverse

from cpho.models import DimensionType, Indicator, IndicatorDatum, Period

from .utils_for_tests import patch_rules


def test_import(hso_client):
    data = {}
    # byte file mimicking a file with the following contents:
    # indicator name = Test Upload
    # 2 data points
    data["csv_file"] = io.BytesIO(
        b'Category,Topic,Indicator,Detailed Indicator,Sub_Indicator_Measurement,Data_Quality,Value,Value_LowerCI,Value_UpperCI,Value_Displayed,SingleYear_TimeFrame,MultiYear_TimeFrame,Dimension_Type,Dimension_Value,Period,Reason_for_Null_Data,Value_Units\r\nHEALTH OUTCOMES,COMMUNICABLE DISEASES,Test Upload,morph cross-platform technologies,embrace best-of-breed applications,CAUTION,78.100478,12.92545,98.81349619,,,,Sex,MALES,CY2021,,PERCENTAGE (CRUDE RATE)\r\nHEALTH OUTCOMES,COMMUNICABLE DISEASES,Test Upload,morph cross-platform technologies,embrace best-of-breed applications,ACCEPTABLE,53.61193482,14.15379785,93.3798263,,,,Age Group,custom value,CY2021,,"RATE PER 10,000 PATIENT DAYS"\r\n'
    )
    data["csv_file"].name = "test.csv"
    url = reverse("upload_indicator")
    with patch_rules(can_upload_indicator=True):
        response = hso_client.post(
            url,
            data=data,
        )
    assert response.status_code == 302
    assert response["Content-Type"] == "text/html; charset=utf-8"

    url = reverse("save_upload")
    with patch_rules(can_upload_indicator=True):
        response = hso_client.post(
            url,
        )
    assert response.status_code == 200

    indicator = Indicator.objects.get(name="Test Upload")
    assert indicator.name == "Test Upload"
    assert len(IndicatorDatum.active_objects.filter(indicator=indicator)) == 2
