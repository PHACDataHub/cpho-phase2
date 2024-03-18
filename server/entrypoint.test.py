import subprocess
import sys

sys.stdout.write("\nRunning tests...\n")
subprocess.run(["coverage", "run", "-m", "pytest"], check=True)

sys.stdout.write("\nCoverage report:\n")
subprocess.run(["coverage", "report", "--show-missing"], check=True)

sys.stdout.write("\nWritting coverage.json...\n")
subprocess.run(
    [
        "coverage",
        "json",
        "-o",
        "/cpho/web/coverage/coverage.json",
        "--pretty-print",
    ],
    check=True,
)
