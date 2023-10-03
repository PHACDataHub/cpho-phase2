"""
WSGI config for cphophase2 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import atexit

from django.core.wsgi import get_wsgi_application

from server.open_telemetry_util import instrument_app_for_open_telemetry

flush_telemetry_callback = instrument_app_for_open_telemetry()
atexit.register(flush_telemetry_callback)

application = get_wsgi_application()
