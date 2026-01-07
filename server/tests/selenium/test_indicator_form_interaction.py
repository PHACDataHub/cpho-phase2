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


def test_indicator_form_interaction(
    live_server, driver, hso_user, force_login
):
    ind = IndicatorFactory()
    url = reverse("edit_indicator", args=[ind.id])

    force_login(hso_user)

    driver.get(live_server.url + url)

    assert "CPHO Phase 2" in driver.title

    english_name_input = get_element(driver, "#id_name")
    french_name_input = get_element(driver, "#id_name_fr")
    fr_visibility_toggle = get_element(driver, "#show_french")
    # check toggle is not checked
    assert not fr_visibility_toggle.get_property("checked")

    # check enlish visible
    assert english_name_input.is_displayed()

    # check french hidden
    assert not french_name_input.is_displayed()

    click_button(driver, "#show_french")
    # check toggle is checked
    assert fr_visibility_toggle.get_property("checked")
    # check french visible
    assert french_name_input.is_displayed()
    # check english still visible
    assert english_name_input.is_displayed()
