import pytest
from decouple import UndefinedValueError

from server.settings_util import (
    DEV_PUBLIC_ENV_FILE_NAME,
    DEV_SECRET_ENV_FILE_NAME,
    PROD_ENV_FILE_NAME,
    get_project_config,
)


def write_env_file(temp_path, env_file_name):
    env_file = temp_path / env_file_name

    content = f"""
    ENV_FILE_USED={env_file_name}
    ENV_SPECIFIC_{env_file_name}=True
    """

    env_file.write_text(content)


def test_get_project_config_uses_prod_exclusively_if_exists(tmp_path):
    write_env_file(tmp_path, PROD_ENV_FILE_NAME)
    write_env_file(tmp_path, DEV_PUBLIC_ENV_FILE_NAME)
    write_env_file(tmp_path, DEV_SECRET_ENV_FILE_NAME)

    config = get_project_config(env_dir=tmp_path)

    assert config("ENV_FILE_USED") == PROD_ENV_FILE_NAME

    # assert that prod env is used exclusively, values from other env files undefined
    with pytest.raises(UndefinedValueError):
        config(f"ENV_SPECIFIC_{DEV_PUBLIC_ENV_FILE_NAME}")

    assert (
        config(
            f"ENV_SPECIFIC_{DEV_PUBLIC_ENV_FILE_NAME}",
            default="can_still_use_defaults",
        )
        == "can_still_use_defaults"
    )


def test_get_project_config_uses_merged_dev_envs_with_priority_for_dev_secret(
    tmp_path,
):
    write_env_file(tmp_path, DEV_PUBLIC_ENV_FILE_NAME)
    write_env_file(tmp_path, DEV_SECRET_ENV_FILE_NAME)

    config = get_project_config(env_dir=tmp_path)

    # assert that priority is given to dev secrets
    assert config("ENV_FILE_USED") == DEV_SECRET_ENV_FILE_NAME

    # assert that contents are merged (can use values from both)
    assert (
        config(f"ENV_SPECIFIC_{DEV_SECRET_ENV_FILE_NAME}", cast=bool) == True
    )
    assert (
        config(f"ENV_SPECIFIC_{DEV_PUBLIC_ENV_FILE_NAME}", cast=bool) == True
    )

    # assert that expected config behaviour still present (errors on undefined, defaults work)
    with pytest.raises(UndefinedValueError):
        config(f"not_real")
    assert (
        config(
            "not_real",
            default="can_still_use_defaults",
        )
        == "can_still_use_defaults"
    )
