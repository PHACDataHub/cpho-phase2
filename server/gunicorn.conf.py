import os

# See https://cloud.google.com/run/docs/tips/python#optimize_gunicorn

# PORT env var is set by Cloud Run
PORT = os.getenv("PORT", "8080")
bind = [f"0.0.0.0:{PORT}"]

# Note: the generally recommended formula is `workers + threads = multiprocessing.cpu_count() * 2 + 1`,
# not totally clear why these google doc tips use 8 threads. Haven't confirmed that `multiprocessing.cpu_count()`
# is accurate in Cloud Run serverless environment anyway (I know JS libraries used to incorrectly detect vCPUs all the time)
workers = 1  # increase this, and possibly decrease threads, if we ever configure a higher CPU count for Cloud Run
threads = 8

timeout = 0  # from the GCP docs: "timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling."

# Preloading is recommended by the GCP docs, with caveats; gotta be aware of what might be preloaded/resources used in the process
# Warning: preloading loads the app before gunicorn forks. This may conflict with potential uses of gunicorn hooks like post_fork.
# E.g. if we use OpenTelemetry's background process based BatchSpanProcessor, then we need to insturment the app from the post_fork hook,
# to get different background processses per processor. Instrumentation needs to happen before the app launches, so in this case preload_app can't be used
preload_app = True

wsgi_app = "server.wsgi:application"
