import os

from decouple import Config, RepositoryEnv, undefined

PROD_ENV_FILE_NAME = ".env.prod"
DEV_PUBLIC_ENV_FILE_NAME = ".env.dev-public"
DEV_SECRET_ENV_FILE_NAME = ".env.dev-secret"


def get_project_config(BASE_DIR):
    try:
        config = Config(
            RepositoryEnv(os.path.join(BASE_DIR, PROD_ENV_FILE_NAME))
        )
    except:

        def dev_config_merged(*args, default=undefined, **kwargs):
            try:
                return Config(
                    RepositoryEnv(
                        os.path.join(BASE_DIR, DEV_SECRET_ENV_FILE_NAME)
                    )
                )(*args, **kwargs)
            except:
                return Config(
                    RepositoryEnv(
                        os.path.join(BASE_DIR, DEV_PUBLIC_ENV_FILE_NAME)
                    )
                )(*args, default, **kwargs)

        config = dev_config_merged

    return config
