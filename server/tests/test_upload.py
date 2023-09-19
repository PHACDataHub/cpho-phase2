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
        b'Category,Topic,Indicator,Detailed Indicator,Sub_Indicator_Measurement,Data_Quality,Value,Value_LowerCI,Value_UpperCI,Value_Displayed,SingleYear_TimeFrame,MultiYear_TimeFrame,Dimension_Type,Dimension_Value,Period,Age_Group_Type,PT_Data_Availability,Value_Units\r\nFACTORS INFLUENCING HEALTH,CHRONIC DISEASES AND MENTAL HEALTH,Test Upload,revolutionize transparent paradigms,enable cross-platform methodologies,ACCEPTABLE,64.6,10.54585501,92.35028406,"PER 1,000 CENSUS INHABITANTS",2020,,Sex,MALES,CY2021,,Available,"DEFINED DAILY DOSE/1,000 CENSUS INHABITANTS"\r\nFACTORS INFLUENCING HEALTH,CHRONIC DISEASES AND MENTAL HEALTH,Test Upload,revolutionize transparent paradigms,enable cross-platform methodologies,GOOD,29.90096716,15.35232957,99.15098,"PER 10,000 PATIENT DAYS",,2010-2021,Age Group,custom value,CY2021,GRADE,Suppressed,"DEFINED DAILY DOSE/1,000 CENSUS INHABITANTS"\r\n'
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
