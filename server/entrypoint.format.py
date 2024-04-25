import subprocess
import sys

subprocess.run(
    ["python", "-m", "black", "--check", "./", "--config", "pyproject.toml"],
    stdout=sys.stdout,
    stderr=sys.stderr,
)
subprocess.run(
    [
        "python",
        "-m",
        "isort",
        "--check",
        "./",
        "--settings-path ",
        "pyproject.toml",
    ],
    stdout=sys.stdout,
    stderr=sys.stderr,
)

subprocess.run(
    [
        "python",
        "-m",
        "djlint",
        "--check",
        "omd",
        "--configuration",
        "pyproject.toml",
    ],
    stdout=sys.stdout,
    stderr=sys.stderr,
)
