"""
Django settings for cphophase2 project.

Generated by 'django-admin startproject' using Django 3.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
import sys
from pathlib import Path

from django.urls import reverse_lazy

from decouple import Config, Csv, RepositoryEnv
from phac_aspc.django.settings import *
from phac_aspc.django.settings.utils import (
    configure_apps,
    configure_middleware,
)

# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Point decouple.Config to the appropriate .env file
try:
    config = Config(RepositoryEnv(os.path.join(BASE_DIR, ".env.prod")))
except:
    config = Config(RepositoryEnv(os.path.join(BASE_DIR, ".env.dev")))


# For security, these test/dev settings should _never_ be used in production!
IS_LOCAL_DEV = config("IS_LOCAL_DEV", cast=bool, default=False)
IS_RUNNING_TESTS = (
    IS_LOCAL_DEV
    and "test" in sys.argv
    or any("pytest" in arg for arg in sys.argv)
)
if IS_LOCAL_DEV:
    # Dev settings
    SESSION_COOKIE_SECURE = False
    DEBUG = config("DEBUG", default=False, cast=bool)
    ENABLE_DEBUG_TOOLBAR = DEBUG and config(
        "ENABLE_DEBUG_TOOLBAR", default=False, cast=bool
    )
    INTERNAL_IPS = (
        config("INTERNAL_IPS", default="") if ENABLE_DEBUG_TOOLBAR else ""
    )

    # Test settings
    if IS_RUNNING_TESTS:
        from . import monkey_patch_for_testing

        TEST_RUNNER = "tests.pytest_test_runner.PytestTestRunner"

else:
    DEBUG = True
    ENABLE_DEBUG_TOOLBAR = False
    INTERNAL_IPS = ""


# Secrets and security
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())

# Additional CORS allowed and CSRF trusted origins should be empty until if/when the app
# is serving a REST/GraphQL API for external consumption
CORS_ALLOWED_ORIGINS = []
CSRF_TRUSTED_ORIGINS = [  # TODO: if the CSRF middleware and tokens were properly configured, this could be empty, right?
    f"https://{host}" for host in ALLOWED_HOSTS
]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# whitenoise configuration
if config(
    "FORCE_WHITENOISE_PROD_BEHAVIOUR", cast=bool, default=(not IS_LOCAL_DEV)
):
    # requires staticfiles dir, run `./manage.py collectstatic --noinput` as needed!
    WHITENOISE_USE_FINDERS = False
    STATICFILES_STORAGE = (
        "whitenoise.storage.CompressedManifestStaticFilesStorage"
    )
else:
    # with this set, you don't need a staticfiles dir. Whitenoise will find and serve static files automatically
    # BUT this doesn't work with caching/compression! Do NOT use this in prod!
    WHITENOISE_USE_FINDERS = True


# Application definition
INSTALLED_APPS = configure_apps(
    [
        "cpho.apps.CphoConfig",
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "whitenoise.runserver_nostatic",
        "django.contrib.staticfiles",
        "graphene_django",
        "django_extensions",
        *(["debug_toolbar"] if ENABLE_DEBUG_TOOLBAR else []),
    ]
)

MIDDLEWARE = configure_middleware(
    [
        "django.middleware.security.SecurityMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
        *(
            [
                "debug_toolbar.middleware.DebugToolbarMiddleware",
            ]
            if ENABLE_DEBUG_TOOLBAR
            else []
        ),
        "django.middleware.locale.LocaleMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        "versionator.middleware.WhodidMiddleware",
    ]
)


LOGIN_URL = "/login"
LOGIN_REDIRECT_URL = reverse_lazy("list_indicators")

ROOT_URLCONF = "server.urls"
APPEND_SLASH = True

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "environment": "cpho.jinja_helpers.environment",
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "extensions": [],
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "server.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT"),
        #   'OPTIONS': {'sslmode': 'require'},
    }
}
if IS_RUNNING_TESTS:
    DATABASES["default"]["TEST"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("TEST_DB_NAME"),
    }


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]
AUTH_USER_MODEL = "cpho.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-ca"

TIME_ZONE = "EST"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# BUSINESS LOGIC CONFIGURATION

CURRENT_YEAR = 2021
