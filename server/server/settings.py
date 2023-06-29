# sourcery skip: raise-specific-error
"""
Django settings for cphophase2 project.

Generated by 'django-admin startproject' using Django 3.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import io
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

from django.urls import reverse_lazy

import environ
import google.auth
from decouple import Csv, config
from google.cloud import secretmanager
from phac_aspc.django.settings import *
from phac_aspc.django.settings.utils import (
    configure_apps,
    configure_middleware,
)

# During tests, modify settings or monkeypatch things
if "test" in sys.argv or any("pytest" in arg for arg in sys.argv):
    from . import monkey_patch_for_testing


# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# [START cloudrun_django_secret_config]
# SECURITY WARNING: don't run with debug turned on in production!
# Change this to "False" when you are ready for production
env = environ.Env(DEBUG=(bool, True))
env_file = os.path.join(BASE_DIR, ".env")

# import os

# from google.cloud import secretmanager

# #------------------------
# # Create a Secret Manager client
# client = secretmanager.SecretManagerServiceClient()

# # Retrieve the project ID from Secret Manager
# name = "projects/{}/secrets/{}/versions/latest".format("pdcp-cloud-006-cpho", "django_settings")
# response = client.access_secret_version(request={"name": name})
# project_id = response.payload.data.decode("UTF-8")

# # # Set the project ID in the environment variable
# os.environ['GOOGLE_CLOUD_PROJECT'] = "pdcp-cloud-006-cpho"

# #------------
# Attempt to load the Project ID into the environment, safely failing on error.
if (os.environ["GOOGLE_CLOUD_PROJECT"] != 'docker'):
    #TODO change to argv
    try:
        _, os.environ["GOOGLE_CLOUD_PROJECT"] = google.auth.default()
    except google.auth.exceptions.DefaultCredentialsError:
        pass
  

if os.path.isfile(env_file):
    # Use a local secret file, if provided
    env.read_env(env_file)

elif os.getenv("GITHUB_WORKFLOW", None):
    # Create local settings if running with CI, for unit testing
    DATABASES = {
        'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'github_actions',
           'USER': 'postgres',
           'PASSWORD': 'postgres',
           'HOST': '127.0.0.1',
           'PORT': '5432',
        }
    }

    placeholder = (
        f"SECRET_KEY=a\n"
        # "GS_BUCKET_NAME=None\n" #If being used for static file storage - if the case, will need to store bucket in GCP Secret Manager as well
        f"DATABASE_URL=sqlite://{os.path.join(BASE_DIR, 'db.sqlite3')}"
    )
    env.read_env(io.StringIO(placeholder))

elif os.environ.get("GOOGLE_CLOUD_PROJECT", None):
    if (os.environ["GOOGLE_CLOUD_PROJECT"]!= "docker"):
        # Pull secrets from Secret Manager
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")

        client = secretmanager.SecretManagerServiceClient()
        settings_name = os.environ.get("SETTINGS_NAME", "django_settings")
        name = f"projects/{project_id}/secrets/{settings_name}/versions/latest"
        payload = client.access_secret_version(name=name).payload.data.decode("UTF-8")

        env.read_env(io.StringIO(payload))
else:
    # raise Exception("No local .env or GOOGLE_CLOUD_PROJECT detected. No secrets found.")
    pass



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = config("SECRET_KEY")
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=False, cast=bool)
ENABLE_DEBUG_TOOLBAR = DEBUG and config(
    "ENABLE_DEBUG_TOOLBAR", default=False, cast=bool
)
INTERNAL_IPS = config("INTERNAL_IPS", default="")
IS_LOCAL_DEV = config("IS_LOCAL_DEV", cast=bool, default=False)
if IS_LOCAL_DEV:
    SESSION_COOKIE_SECURE = False

CLOUDRUN_SERVICE_URL = env("CLOUDRUN_SERVICE_URL", default=None)
if CLOUDRUN_SERVICE_URL:
    ALLOWED_HOSTS = [urlparse(CLOUDRUN_SERVICE_URL).netloc]
    CSRF_TRUSTED_ORIGINS = [CLOUDRUN_SERVICE_URL]
else:
    ALLOWED_HOSTS =  ["*"]
# ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())
    CORS_ALLOWED_ORIGINS = ["*"]

# Application definition
INSTALLED_APPS = configure_apps(
    [
        "cpho.apps.CphoConfig",
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "whitenoise.runserver_nostatic",
        "graphene_django",
        "django_extensions",
        *(["debug_toolbar"] if ENABLE_DEBUG_TOOLBAR else []),
    ]
)

# STATIC_URL = "/static/"
# STATICFILES_DIRS = (os.path.join("static"),)
# STATIC_ROOT = BASE_DIR / "staticfiles"

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
# STATICFILES_DIR = [str(BASE_DIR.joinpath('static'))]
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_ROOT =os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# when upgrade django >=4.2
# STORAGES = {
#     "staticfiles": {
#         "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
#     },
# }

MIDDLEWARE = configure_middleware(
    [
        *(
            [
                "debug_toolbar.middleware.DebugToolbarMiddleware",
            ]
            if ENABLE_DEBUG_TOOLBAR
            else []
        ),
        "django.middleware.locale.LocaleMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
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
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
# Set this value from django-environ
DATABASES = {"default": env.db()}

# Change database settings if using the Cloud SQL Auth Proxy
if os.getenv("USE_CLOUD_SQL_AUTH_PROXY", None):
    DATABASES["default"]["HOST"] = "127.0.0.1"
    DATABASES["default"]["PORT"] = 5432
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": config("DB_NAME"),
#         "USER": config("DB_USER"),
#         "PASSWORD": config("DB_PASSWORD"),
#         "HOST": config("DB_HOST"),
#         "PORT": config("DB_PORT"),
#         #   'OPTIONS': {'sslmode': 'require'},
#         "TEST": {
#             "ENGINE": "django.db.backends.postgresql",
#             "NAME": config("TEST_DB_NAME", default="cpho_test_db"),
#         },
#     }
# # Database
# # https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": config("DB_NAME"),
#         "USER": config("DB_USER"),
#         "PASSWORD": config("DB_PASSWORD"),
#         "HOST": config("DB_HOST"),
#         "PORT": config("DB_PORT"),
#         #   'OPTIONS': {'sslmode': 'require'},
#         "TEST": {
#             "ENGINE": "django.db.backends.postgresql",
#             "NAME": config("TEST_DB_NAME", default="cpho_test_db"),
#         },
#     }
# }

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]
AUTH_USER_MODEL = "cpho.User"

TEST_RUNNER = "tests.pytest_test_runner.PytestTestRunner"

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-ca"

TIME_ZONE = "EST"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# CORS_ALLOWED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:8000"]

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# BUSINESS LOGIC CONFIGURATION

CURRENT_YEAR = 2021
