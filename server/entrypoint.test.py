import os
import subprocess
import sys

sys.stdout.write("\nRunning tests...\n")
subprocess.run(
    ["python", "-m", "coverage", "run", "-m", "pytest"],
    check=True,
    stdout=sys.stdout,
    stderr=sys.stderr,
)

sys.stdout.write("\nCoverage report:\n")
subprocess.run(
    ["python", "-m", "coverage", "report", "--show-missing"],
    check=True,
    stdout=sys.stdout,
    stderr=sys.stderr,
)

sys.stdout.write("\nWritting coverage.json...\n")
subprocess.run(
    [
        "python",
        "-m",
        "coverage",
        "json",
        "-o",
        # NOTE: docker-compose.run-tests.yaml mounts a volume from the host system
        # to /cpho/web/coverage, to make sharing the coverage.json easier. This volume
        # must be globally writable for this script to run
        "/cpho/web/coverage/coverage.json",
        "--pretty-print",
    ],
    check=True,
    stdout=sys.stdout,
    stderr=sys.stderr,
)
