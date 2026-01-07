from django.contrib.auth.models import Group
from django.core.management import call_command
from django.db import transaction
from django.test.client import Client

import pytest
from jinja2 import Template as Jinja2Template
from phac_aspc.django.settings.utils import configure_settings_for_tests

from cpho import constants
from cpho.management.commands.seed_countries import seed_countries
from cpho.models import User

# Modify django settings to skip axes authentication backend
configure_settings_for_tests()


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    without this, tests (including old-style) have to explicitly declare db as a dependency
    https://pytest-django.readthedocs.io/en/latest/faq.html#how-can-i-give-database-access-to-all-my-tests-without-the-django-db-marker
    """
    pass


@pytest.fixture(scope="session")
def globally_scoped_fixture_helper(
    django_db_setup, django_db_blocker, request
):

    # If ANY collected test is marked selenium, don't do the global atomic trick.
    if (
        request.config.getoption("-m", default="")
        and "selenium" in request.config.getoption("-m")
        and "not selenium" not in request.config.getoption("-m")
    ):
        print("Activating selenium transaction mode")
        with django_db_blocker.unblock():
            yield
        return

    else:
        with django_db_blocker.unblock():
            # Wrap in try + atomic block to do non crashing rollback
            # This means we don't have to re-create a test DB each time
            try:
                with transaction.atomic():
                    yield
                    raise Exception
            except Exception:
                pass


@pytest.fixture(scope="session", autouse=True)
def seed_core_data_fixture(globally_scoped_fixture_helper):
    print("Seeding core data...")
    call_command("loaddata", "cpho/fixtures/periods.yaml")
    call_command("loaddata", "cpho/fixtures/dimension_lookups.yaml")
    seed_countries(mode="reset")
    Group.objects.get_or_create(name=constants.ADMIN_GROUP_NAME)


@pytest.fixture
def vanilla_user():
    return User.objects.create(username="vanilla_user")


@pytest.fixture
def vanilla_user_client(vanilla_user):
    client = Client()
    client.force_login(vanilla_user)
    return client


@pytest.fixture
def hso_user():
    hso = User.objects.create_user(
        username="hso",
        password="hso",
    )
    group, _ = Group.objects.get_or_create(name=constants.HSO_GROUP_NAME)
    hso.groups.add(group)
    return hso


@pytest.fixture
def hso_client(hso_user):
    client = Client()
    client.force_login(hso_user)
    return client


@pytest.fixture
def oae_lead_client(oae_lead):
    client = Client()
    client.force_login(oae_lead)
    return client
