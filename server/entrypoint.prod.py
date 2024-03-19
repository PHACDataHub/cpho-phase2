import subprocess
import sys

# I'd love for this to be a Docker build time step, but there's subtle differences to the
# output depending on if this is running with dev or prod env vars is used, so it
# has to happen after the prod env have been (potentially) injected at run time
sys.stdout.write("\nRunning collectstatic...\n")
subprocess.run(
    ["python", "./manage.py", "collectstatic", "--no-input"], check=True
)

sys.stdout.write("\nApplying migrations...\n")
subprocess.run(["python", "./manage.py", "migrate"], check=True)

sys.stdout.write("\nStarting gunicorn\n")
# https://docs.gunicorn.org/en/latest/custom.html#direct-usage-of-existing-wsgi-apps
subprocess.run(["python", "-m", "gunicorn"])
