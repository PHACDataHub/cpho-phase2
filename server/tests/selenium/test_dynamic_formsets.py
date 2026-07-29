# this is a bunch of meta tests

from django.urls import reverse

import pytest

from cpho.model_factories import IndicatorFactory
from cpho.models import DimensionType, Indicator, Period

from .selenium_util import click_button, get_element, get_elements

# tag the whole module
pytestmark = [
    pytest.mark.selenium,
    pytest.mark.django_db(transaction=True),
]


def test_dynamic_agegroup_formset(live_server, driver, hso_user, force_login):

    period = Period.objects.first()
    ind = IndicatorFactory()
    age_group_dim = DimensionType.objects.get(code="age")

    record0_25 = ind.data.create(
        period=period,
        dimension_type=age_group_dim,
        literal_dimension_val="0-25",
        value=5,
    )

    url = reverse(
        "manage_indicator_data", args=[ind.id, period.id, age_group_dim.pk]
    )

    force_login(hso_user)

    driver.get(live_server.url + url)

    assert "CPHO Phase 2" in driver.title

    original_form_count = len(
        get_elements(driver, "form table tr.age-group-form")
    )
    assert original_form_count == 2  # one existing + one empty form

    click_button(driver, "#add-form")

    new_form_count = len(get_elements(driver, "form table tr.age-group-form"))
    assert new_form_count == original_form_count + 1


def test_dynamic_trend_formset(live_server, driver, hso_user, force_login):

    period = Period.objects.first()
    ind = IndicatorFactory()

    url = reverse("manage_trend_analysis_data", args=[ind.id])

    force_login(hso_user)

    driver.get(live_server.url + url)

    assert "CPHO Phase 2" in driver.title

    original_form_count = len(
        get_elements(driver, "form table tr.trend-analysis-form")
    )
    assert original_form_count == 1  # just an empty form

    click_button(driver, "#add-form")

    new_form_count = len(
        get_elements(driver, "form table tr.trend-analysis-form")
    )
    assert new_form_count == original_form_count + 1


def test_dynamic_benchmarking_formset(
    live_server, driver, hso_user, force_login
):

    period = Period.objects.first()
    ind = IndicatorFactory()

    url = reverse("manage_benchmarking_data", args=[ind.id])

    force_login(hso_user)

    driver.get(live_server.url + url)

    assert "CPHO Phase 2" in driver.title

    original_form_count = len(
        get_elements(driver, "form table tr.benchmarking-form")
    )
    assert original_form_count == 1  # just an empty form

    click_button(driver, "#add-form")

    new_form_count = len(
        get_elements(driver, "form table tr.benchmarking-form")
    )
    assert new_form_count == original_form_count + 1
