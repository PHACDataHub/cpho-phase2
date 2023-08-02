import os

from server.open_telemetry_util import instrument_app_for_open_telemetry

# See https://cloud.google.com/run/docs/tips/python#optimize_gunicorn

# PORT env var is set by Cloud Run
PORT = os.getenv("PORT", "8080")
bind = [f"0.0.0.0:{PORT}"]

# Note: the generally recommended formula is `workers + threads = cpu_count * 2 + 1`, although gunicorn  describes this as "not overly scientific".
# Cloud Run only has one vCPU by default, but Google doc Cloud Run gunicorn examples configure one worker and 8 threads consistently
workers = 1  # increase this, and potentially adjust threads, if we ever configure a higher CPU count for Cloud Run
threads = 4  # half of what GCP examples use, as each of our app process will use at least two threads (app thread + BatchSpanProcessor worker thread)

timeout = 0  # from the GCP docs: "timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling."

# Preloading is recommended by the GCP docs, with caveats; gotta be aware of what might be preloaded/resources used in the process/any gunicorn hooks used
# Warning: preloading loads the app before gunicorn forks, meaning it's NOT compatible with situations where some initialization must occur in a post_fork hook
# preload_app = True


def post_fork(server, worker):
    # When using OpenTelemetry's background process based BatchSpanProcessor, insturmentation must occur post worker forking. Pre-fork instrumentation
    # would result in each app process trying to share the same BatchSpanProcessor worker thread, which would not be reliable.
    # If NOT using BatchSpanProcessor (likely a bad idea, it's much more performant at run time) you can move instrumentation to wsgi.py and enable preload_app
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

    worker.flush_telemetry_callback = instrument_app_for_open_telemetry()


def worker_exit(server, worker):
    try:
        worker.flush_telemetry_callback()
    except AttributeError:
        worker.log.error(
            "Worker does not have expected flush_telemetry_callback function"
        )


wsgi_app = "server.wsgi:application"
