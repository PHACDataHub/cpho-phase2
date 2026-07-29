from django.conf import settings
from django.contrib.auth import (
    BACKEND_SESSION_KEY,
    HASH_SESSION_KEY,
    SESSION_KEY,
)
from django.contrib.sessions.backends.db import SessionStore

import pytest


# override the global autouse fixture just for selenium tests in this package
# see tests/conftest.py's enable_db_access_for_all_tests
@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(transactional_db):
    pass


@pytest.fixture(scope="session")
def driver():
    from selenium import webdriver

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    d = webdriver.Chrome(options=options)
    yield d
    d.quit()


@pytest.fixture
def force_login(driver, live_server):
    """
    Returns a function: force_login(user) that logs the browser in by setting session cookie.
    """

    def _force_login(user):
        # 1) create a session in Django
        session = SessionStore()
        session[SESSION_KEY] = str(user.pk)
        session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
        session[HASH_SESSION_KEY] = user.get_session_auth_hash()
        session.save()

        # 2) visit domain once so Selenium is allowed to set cookies
        driver.get(live_server.url + "/404-does-not-exist")

        # 3) set the session cookie in the browser
        driver.add_cookie(
            {
                "name": settings.SESSION_COOKIE_NAME,
                "value": session.session_key,
                "path": "/",
            }
        )

    return _force_login
