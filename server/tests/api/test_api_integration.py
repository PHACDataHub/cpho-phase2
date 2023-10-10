from django.urls import reverse

query = """
query {
  indicators{
    name
    id
    detailedIndicator
    subIndicatorMeasurement    
    data(year:2022){
      value
      literalDimensionVal
      dataQuality
      reasonForNull
      valueUnit
      valueDisplayed
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


def test_query_api_via_http(client):
    """
    We're just testing that the view is wired up correctly
    Inspecting that data is correct is done in more unit-style tests
    """

    url = reverse("graphql")
    response = client.post(url, {"query": query})
    assert response.status_code == 200
    json = response.json()
    assert "indicators" in json["data"]
