# this is a bunch of meta tests

from django.urls import reverse

import pytest

from cpho.models import User

# tag the whole module
pytestmark = [
    pytest.mark.selenium,
    pytest.mark.django_db(transaction=True),
]


# first, check that tests are working with independent DBs
def test_selenium_isolated_db_one(live_server, driver):
    u = User.objects.create(username="testuser")


def test_selenium_isolated_db_two(live_server, driver):
    # without isolation, this would fail uniqueness constraint
    u = User.objects.create(username="testuser")


def test_login_works(live_server, driver, hso_user, force_login):
    force_login(hso_user)

    driver.get(live_server.url + reverse("list_indicators"))
    # result = driver.get(live_server.url + reverse("list_users"))
    # div = driver.find_element(By.TAG_NAME, "div")

    assert "CPHO Phase 2" in driver.title
    assert "login" not in driver.title.lower()
