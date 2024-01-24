from django.urls import reverse

from cpho.model_factories import IndicatorDatumFactory, IndicatorFactory
from cpho.models import TrendAnalysis

from .utils_for_tests import patch_rules


def test_trend_analysis(vanilla_user_client):
    ind = IndicatorFactory()
    ind.save()
    url = reverse("manage_trend_analysis_data", args=[ind.id])

    with patch_rules(can_edit_trend_analysis=True):
        response = vanilla_user_client.get(url)
        assert response.status_code == 200

    data = {
        "trend_analysis-TOTAL_FORMS": 2,
        "trend_analysis-INITIAL_FORMS": 0,
        "trend_analysis-MIN_NUM_FORMS": 0,
        "trend_analysis-MAX_NUM_FORMS": 1000,
        "trend_analysis-0-year": "2020",
        "trend_analysis-0-year_range": "2019-2020",
        "trend_analysis-0-data_point": 9.9,
        "trend_analysis-0-trend_segment": "2019-2020",
        "trend_analysis-0-trend": TrendAnalysis.TREND_CHOICES[1][0],
        "trend_analysis-1-year": "2021",
        "trend_analysis-1-year_range": "2020-2021",
        "trend_analysis-1-data_point": 10.9,
        "trend_analysis-1-trend_segment": "2020-2021",
        "trend_analysis-1-trend": TrendAnalysis.TREND_CHOICES[2][0],
    }

    with patch_rules(can_edit_trend_analysis=True):
        response = vanilla_user_client.post(url, data=data)
        assert response.status_code == 302

    created_data = TrendAnalysis.active_objects.filter(indicator=ind)
    assert created_data.count() == 2
    data2020 = created_data.get(year="2020")
    assert data2020.year_range == "2019-2020"
    assert data2020.data_point == 9.9
    assert data2020.trend_segment == "2019-2020"
    assert data2020.trend == TrendAnalysis.TREND_CHOICES[1][0]
    data2021 = created_data.get(year="2021")
    assert data2021.year_range == "2020-2021"
    assert data2021.data_point == 10.9
    assert data2021.trend_segment == "2020-2021"
    assert data2021.trend == TrendAnalysis.TREND_CHOICES[2][0]

    with patch_rules(can_edit_trend_analysis=True):
        response = vanilla_user_client.get(url)
        assert response.status_code == 200

    data = {
        "trend_analysis-TOTAL_FORMS": 2,
        "trend_analysis-INITIAL_FORMS": 2,
        "trend_analysis-MIN_NUM_FORMS": 0,
        "trend_analysis-MAX_NUM_FORMS": 1000,
        "trend_analysis-0-id": data2020.id,
        "trend_analysis-0-year": "2020",
        "trend_analysis-0-year_range": "2019-2020",
        "trend_analysis-0-data_point": 9.0,
        "trend_analysis-0-trend_segment": "2019-2020",
        "trend_analysis-0-trend": TrendAnalysis.TREND_CHOICES[1][0],
        "trend_analysis-1-id": data2021.id,
        "trend_analysis-1-year": "2021",
        "trend_analysis-1-year_range": "2020-2021",
        "trend_analysis-1-data_point": 10.9,
        "trend_analysis-1-trend_segment": "2020-2021",
        "trend_analysis-1-trend": TrendAnalysis.TREND_CHOICES[2][0],
        "trend_analysis-1-is_deleted": "on",  # delete 2022
    }
