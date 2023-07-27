import os

from server.open_telemetry_util import instrument_app


def post_fork(server, worker):
    # Need to set "DJANGO_SETTINGS_MODULE" before instrumenting, and it's suggested to
    # instrument first thing after setting it, so this is the most sensible place for it
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

    instrument_app()
