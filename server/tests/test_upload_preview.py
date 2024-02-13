import io

from django.urls import reverse

from bs4 import BeautifulSoup

from cpho.models import DimensionType, Indicator, IndicatorDatum, Period

from .utils_for_tests import patch_rules


def check_preview(val_dict, hso_client, fieldname=None, num_errors=1):
    data_header = "Category,Topic,Indicator,Detailed Indicator,Sub_Indicator_Measurement,Data_Quality,Value,Value_LowerCI,Value_UpperCI,Value_Displayed,SingleYear_TimeFrame,MultiYear_TimeFrame,Dimension_Type,Dimension_Value,Period,Reason_for_Null_Data,Value_Units\r\n"
    if fieldname:
        correct_category_val = val_dict[fieldname]
        val_dict[fieldname] = "incorrect data"
    data_row = f"{val_dict['category']},{val_dict['topic']},{val_dict['indicator']},{val_dict['detailed_indicator']},{val_dict['sub_indicator_measurement']},{val_dict['data_quality']},{val_dict['value']},{val_dict['value_lower_ci']},{val_dict['value_upper_ci']},{val_dict['value_displayed']},{val_dict['single_year_time_frame']},{val_dict['multi_year_time_frame']},{val_dict['dimension_type']},{val_dict['dimension_value']},{val_dict['period']},{val_dict['reason_for_null']},{val_dict['value_units']}\r\n"
    file_data = data_header + data_row
    if fieldname:
        val_dict[fieldname] = correct_category_val
    data = {}
    data["csv_file"] = io.BytesIO(file_data.encode("utf-8"))
    data["csv_file"].name = "test.csv"

    url = reverse("upload_indicator")
    with patch_rules(can_use_indicator_upload=True):
        response = hso_client.post(
            url,
            data=data,
            follow=True,
        )
    assert response.status_code == 200
    html_content = response.content.decode("utf-8")
    soup = BeautifulSoup(html_content, "html.parser")
    upload_btn = soup.find(id="upload-btn")
    assert upload_btn is not None
    if fieldname:
        assert upload_btn.has_attr("disabled")
    else:
        assert not upload_btn.has_attr("disabled")

    error_preview = soup.find_all(class_="error-preview")
    if fieldname:
        assert error_preview is not None
        assert len(error_preview) == num_errors
    else:
        assert error_preview == []


def test_preview(hso_client):
    val_dict = {
        "category": "HEALTH OUTCOMES",
        "topic": "COMMUNICABLE DISEASES",
        "indicator": "Test Upload",
        "detailed_indicator": "morph cross-platform technologies",
        "sub_indicator_measurement": "embrace best-of-breed applications",
        "data_quality": "CAUTION",
        "value": "78.100478",
        "value_lower_ci": "12.92545",
        "value_upper_ci": "98.81349619",
        "value_displayed": "%",
        "single_year_time_frame": "2021",
        "multi_year_time_frame": "",
        "dimension_type": "Sex",
        "dimension_value": "MALES",
        "period": "CY2021",
        "reason_for_null": "",
        "value_units": "PERCENTAGE",
    }
    check_preview(val_dict, hso_client, "category")
    check_preview(val_dict, hso_client, "topic")
    check_preview(val_dict, hso_client, "data_quality")
    check_preview(val_dict, hso_client, "value_displayed")
    check_preview(val_dict, hso_client, "period")
    check_preview(val_dict, hso_client, "reason_for_null")
    check_preview(val_dict, hso_client, "value_units")
    check_preview(val_dict, hso_client, "dimension_type", num_errors=2)
    check_preview(val_dict, hso_client, "dimension_value")

    check_preview(val_dict, hso_client)
