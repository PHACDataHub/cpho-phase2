import os
from collections import ChainMap

from decouple import Config, RepositoryEnv

ENV_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROD_ENV_FILE_NAME = ".env.prod"
DEV_SECRET_ENV_FILE_NAME = ".env.dev-secret"
DEV_PUBLIC_ENV_FILE_NAME = ".env.dev-public"


# Reminder: decouple config(...) looks in OS env vars first, configured env file second
def get_project_config(
    env_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
):
    def get_env_file(env_file_name):
        return RepositoryEnv(os.path.join(env_dir, env_file_name))

    try:
        # If the prod env file exists, use it exclusively
        config = Config(get_env_file(PROD_ENV_FILE_NAME))
    except FileNotFoundError:
        try:
            # If both the secret and public dev env files exist, use both (with preference for values in the secret file)
            config = Config(
                ChainMap(
                    get_env_file(DEV_SECRET_ENV_FILE_NAME),
                    get_env_file(DEV_PUBLIC_ENV_FILE_NAME),
                )
            )
        except FileNotFoundError:
            # If neither the prod nor secret dev files exist, just use the public dev env file
            config = Config(get_env_file(DEV_PUBLIC_ENV_FILE_NAME))

    return config
