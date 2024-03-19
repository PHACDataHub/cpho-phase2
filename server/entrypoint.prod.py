import subprocess
import sys

# I'd love for this to be a Docker build time step, but there's subtle differences to the
# output depending on if this is running with dev or prod env vars is used, so it
# has to happen after the prod env have been (potentially) injected at run time
subprocess.run(
    ["python", "./manage.py", "collectstatic", "--no-input"],
    check=True,
    stdout=sys.stdout,
    stderr=sys.stderr,
)

subprocess.run(
    ["python", "./manage.py", "migrate"],
    check=True,
    stdout=sys.stdout,
    stderr=sys.stderr,
)

# https://docs.gunicorn.org/en/latest/custom.html#direct-usage-of-existing-wsgi-apps
subprocess.run(
    ["python", "-m", "gunicorn"],
    check=True,
    stdout=sys.stdout,
    stderr=sys.stderr,
)
