import os

from decouple import Config, RepositoryEnv, UndefinedValueError, undefined

PROD_ENV_FILE_NAME = ".env.prod"
DEV_PUBLIC_ENV_FILE_NAME = ".env.dev-public"
DEV_SECRET_ENV_FILE_NAME = ".env.dev-secret"


# Reminder: decouple config(...) looks in OS env vars first, configured env file second
def get_project_config(BASE_DIR):
    try:
        # If the prod env file exists, use it exclusively
        config = Config(
            RepositoryEnv(os.path.join(BASE_DIR, PROD_ENV_FILE_NAME))
        )
    except FileNotFoundError:
        # If the prod env file doesn't exist
        #   1) look for the secret in the dev-secret env file
        #   2) if the dev-secret env file doesn't exist OR the the secret isn't
        #      found in it, look in the dev-public file
        #   3) if still not found, fall back to provided `default` (if any)

        # IMPORTANT: dev_config_merged must support the API of decouple's config function! Masquerades as it in use
        def dev_config_merged(*args, default=undefined, **kwargs):
            try:
                # Note that the `default` value is not propogated to the dev-secret call,
                # else the default would be returned without looking in dev-public
                return Config(
                    RepositoryEnv(
                        os.path.join(BASE_DIR, DEV_SECRET_ENV_FILE_NAME)
                    )
                )(*args, **kwargs)
            except (FileNotFoundError, UndefinedValueError):
                return Config(
                    RepositoryEnv(
                        os.path.join(BASE_DIR, DEV_PUBLIC_ENV_FILE_NAME)
                    )
                )(*args, default, **kwargs)

        config = dev_config_merged

    return config
