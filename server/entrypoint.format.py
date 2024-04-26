import subprocess
import sys

subprocess.run(
    ["python", "-m", "black", "--check", "./", "--config", "pyproject.toml"],
    check=True,
    stdout=sys.stdout,
    stderr=sys.stderr,
)
# subprocess.run(
#     [
#         "python",
#         "-m",
#         "isort",
#         "--check",
#         "./",
#         "--settings-path ",
#         "pyproject.toml",
#     ],
#     check=True,
#     stdout=sys.stdout,
#     stderr=sys.stderr,
# )

subprocess.run(
    [
        "python",
        "-m",
        "djlint",
        "--check",
        "./",
        "--configuration",
        "pyproject.toml",
    ],
    check=True,
    stdout=sys.stdout,
    stderr=sys.stderr,
)
