import os
import subprocess
import sys

sys.stdout.write("\nRunning tests...\n")
subprocess.run(["python", "-m", "coverage", "run", "-m", "pytest"], check=True)

sys.stdout.write("\nCoverage report:\n")
subprocess.run(
    ["python", "-m", "coverage", "report", "--show-missing"], check=True
)

sys.stdout.write("\nWritting coverage.json...\n")
app_home = os.environ["APP_HOME"]
subprocess.run(
    [
        "python",
        "-m",
        "coverage",
        "json",
        "-o",
        f"{app_home}/coverage.json",
        "--pretty-print",
    ],
    check=True,
)
