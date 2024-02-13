import os

# See https://cloud.google.com/run/docs/tips/python#optimize_gunicorn

PORT = os.getenv("PORT", "8080")
bind = [f"0.0.0.0:{PORT}"]

# Experiment: trying k8s pods deployed with the minimal resources, and only one Django instance per container
workers = 1
threads = 1

# From the GCP docs: "timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling."
# Assume it's of simillar benefit with GKE Autopilot, TODO: determine if that's true
timeout = 0

wsgi_app = "server.wsgi:application"
