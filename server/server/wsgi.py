"""
WSGI config for cphophase2 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from server.open_telemetry_util import instrument_app_for_open_telemetry

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

instrument_app_for_open_telemetry()

application = get_wsgi_application()
