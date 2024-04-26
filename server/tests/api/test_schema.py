from cpho.model_factories import IndicatorFactory
from cpho.models import DimensionType, DimensionValue, Period

from tests.api.api_test_utils import execute_query
from tests.utils_for_tests import submit_indicator_datum

query = """
query SingleIndicator($id: Int!) {
    indicator(id: $id) {
        name
        data(year:2021){
            value
            dimensionValue {
                id
                value
                nameEn
            }
            dimensionType {
                id
                nameEn
            }
            period {
                year
                quarter
                yearType
            }
        }
    }
}
"""


def test_execute_indicator_query():
    y2021 = Period.objects.get(
        year=2021, quarter=None, year_type=Period.CALENDAR_YEAR_TYPE
    )
    dim = DimensionType.objects.first()
    dim_val = dim.possible_values.first()
    ind = IndicatorFactory(name="test")
    datum = ind.data.create(
        period=y2021,
        dimension_type=dim,
        dimension_value=dim_val,
        value=123,
    )
    submit_indicator_datum(datum)

    data = execute_query(query, {"id": ind.id})
    assert data["indicator"]["name"] == "test"
    assert len(data["indicator"]["data"]) == 1
    assert data["indicator"]["data"][0]["value"] == 123
    period_data = data["indicator"]["data"][0]["period"]

    assert period_data["year"] == 2021
    assert period_data["quarter"] is None
    assert period_data["yearType"] == "CALENDAR"

    dim_type_data = data["indicator"]["data"][0]["dimensionType"]
    assert int(dim_type_data["id"]) == dim.id
    assert dim_type_data["nameEn"] == dim.name_en

    dim_val_data = data["indicator"]["data"][0]["dimensionValue"]
    assert int(dim_val_data["id"]) == dim_val.id
    assert dim_val_data["value"] == dim_val.value
    assert dim_val_data["nameEn"] == dim_val.name_en
