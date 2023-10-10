import os
import sys
from collections import ChainMap

from decouple import Config, RepositoryEmpty, RepositoryEnv

ENV_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEV_SECRET_ENV_FILE_NAME = ".env.dev-secret"
DEV_PUBLIC_ENV_FILE_NAME = ".env.dev-public"


def is_running_tests():
    return "test" in sys.argv or any("pytest" in arg for arg in sys.argv)


# Reminder: decouple config(...) looks in OS env vars first, configured env file second
def get_project_config(
    env_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
):
    if os.getenv("IS_K8S"):
        # In our k8s deployments, env vars are injected in to the container via
        # the app server's deployment.yaml. When in a k8s environment, we just
        # use Config as a wrapper for accessing OS env vars, by providing an
        # empty repo env object
        return Config(RepositoryEmpty())

    def get_env_file(env_file_name):
        return RepositoryEnv(os.path.join(env_dir, env_file_name))

    try:
        # If both the secret and public dev env files exist, use both (with preference for values in the secret file)
        config = Config(
            ChainMap(
                get_env_file(DEV_SECRET_ENV_FILE_NAME),
                get_env_file(DEV_PUBLIC_ENV_FILE_NAME),
            )
        )
    except FileNotFoundError:
        # Fallback to just the public dev env file
        config = Config(get_env_file(DEV_PUBLIC_ENV_FILE_NAME))

    return config
