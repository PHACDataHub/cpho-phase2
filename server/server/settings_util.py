import os

from decouple import Config, RepositoryEnv, UndefinedValueError, undefined

PROD_ENV_FILE_NAME = ".env.prod"
DEV_PUBLIC_ENV_FILE_NAME = ".env.dev-public"
DEV_SECRET_ENV_FILE_NAME = ".env.dev-secret"


# Reminder: decouple config(...) looks in OS env vars first, configured env file second
def get_project_config(BASE_DIR):
    try:
        # If the prod env file exists, use it exclusively
        return Config(
            RepositoryEnv(os.path.join(BASE_DIR, PROD_ENV_FILE_NAME))
        )
    except FileNotFoundError:
        dev_public_config = Config(
            RepositoryEnv(os.path.join(BASE_DIR, DEV_PUBLIC_ENV_FILE_NAME))
        )

        # If the dev-secret env file doesn't exist, just use the dev-public config
        try:
            dev_secret_config = Config(
                RepositoryEnv(os.path.join(BASE_DIR, DEV_SECRET_ENV_FILE_NAME))
            )
        except FileNotFoundError:
            return dev_public_config

        # If the dev-secret env file DOES exist, use a wrapper to effectively merge it with dev-public:
        #  1) look for the secret in the dev-secret env file
        #  3) if not found in dev-secret, look in the dev-public file
        #  4) if still not found, fall back to provided `default` (if any)
        # IMPORTANT: dev_merged_config must support the API of decouple's `config`! Masquerades as it in use
        def dev_merged_config(*args, default=undefined, **kwargs):
            try:
                # Note that the `default` value is not propogated to the dev_secret_config call,
                # else the default would be returned here without looking in dev-public
                return dev_secret_config(*args, **kwargs)
            except UndefinedValueError:
                return dev_public_config(*args, default, **kwargs)

        return dev_merged_config
