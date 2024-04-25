import subprocess
import sys

subprocess.run(
    ["black", "--check", "./", "--config", "pyproject.toml"],
    check=True,
    stdout=sys.stdout,
    stderr=sys.stderr,
)
subprocess.run(
    ["isort", "--check", "./", "--settings-path ", "pyproject.toml"],
    check=True,
    stdout=sys.stdout,
    stderr=sys.stderr,
)

subprocess.run(
    ["djlint", "--check", "omd", "--configuration", "pyproject.toml"],
    check=True,
    stdout=sys.stdout,
    stderr=sys.stderr,
)
