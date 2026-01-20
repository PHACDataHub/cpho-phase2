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
        b"Category,Topic,Indicator,Detailed Indicator,Sub_Indicator_Measurement,Data_Quality,Value,Value_LowerCI,Value_UpperCI,Value_Displayed,SingleYear_TimeFrame,MultiYear_TimeFrame,Dimension_Type,Dimension_Value,Period,Reason_for_Null_Data,Value_Units,Arrow_Flag\r\n"
        b"FACTORS INFLUENCING HEALTH,SOCIAL FACTORS,Test Upload,strategize e-business supply-chains,revolutionize cross-media e-business,ACCEPTABLE,58.98178803,5.65398,83.99,%,,,Sex,MALES,CY2022,Suppressed,PERCENTAGE (CRUDE),UP\r\n"
        b'FACTORS INFLUENCING HEALTH,SOCIAL FACTORS,Test Upload,strategize e-business supply-chains,revolutionize cross-media e-business,,60.611,6.78,95.178702,%,,,Sex,FEMALES,CY2022,Not available,"RATE PER 100,000 POPULATION PER YEAR",DOWN\r\n'
        b'FACTORS INFLUENCING HEALTH,SOCIAL FACTORS,Test Upload,strategize e-business supply-chains,revolutionize cross-media e-business,,7,6,95.178702,%,,,Age Group,20-30,CY2022,Not available,"RATE PER 100,000 POPULATION PER YEAR",DOWN\r\n'
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
    assert len(IndicatorDatum.active_objects.filter(indicator=indicator)) == 3

    female_record = IndicatorDatum.active_objects.get(
        indicator=indicator, dimension_value__value="f"
    )
    assert female_record.dimension_type == DimensionType.objects.get(
        code="sex"
    )
    assert female_record.literal_dimension_val is None
    assert female_record.value == 60.611

    age_group_record = IndicatorDatum.active_objects.get(
        indicator=indicator, dimension_type__code="age"
    )
    assert age_group_record.literal_dimension_val == "20-30"
    assert age_group_record.dimension_type == DimensionType.objects.get(
        code="age"
    )
    assert age_group_record.dimension_value is None
    assert age_group_record.value == 7.0
