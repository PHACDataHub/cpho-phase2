import os
import subprocess
import sys

subprocess.run(
    [
        "python",
        "-m",
        "coverage",
        "run",
        "-m",
        "pytest",
    ],
    check=True,
    stdout=sys.stdout,
    stderr=sys.stderr,
)

subprocess.run(
    ["python", "-m", "coverage", "report", "--show-missing"],
    check=True,
    stdout=sys.stdout,
    stderr=sys.stderr,
)

app_home_dir = os.environ["APP_HOME"]
subprocess.run(
    [
        "python",
        "-m",
        "coverage",
        "json",
        "-o",
        # NOTE: "{app_home_dir}/coverage" is expected to be a writable mounted volume, see docker-compose.run-tests.yaml.
        # Used to share the coverage report with the host system.
        f"{app_home_dir}/coverage/coverage.json",
        "--pretty-print",
    ],
    check=True,
    stdout=sys.stdout,
    stderr=sys.stderr,
)
