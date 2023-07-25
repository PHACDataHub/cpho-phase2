import os
import sys

import pytest
from decouple import UndefinedValueError

from server.config_util import (
    DEV_PUBLIC_ENV_FILE_NAME,
    DEV_SECRET_ENV_FILE_NAME,
    PROD_ENV_FILE_NAME,
    get_project_config,
    is_running_tests,
)


def write_env_file(temp_path, env_file_name):
    env_file = temp_path / env_file_name

    content = f"""
    ENV_FILE_USED={env_file_name}
    ENV_SPECIFIC_{env_file_name}=True
    """

    env_file.write_text(content)


def test_is_running_tests_returns_true_inside_test_execution_environment():
    assert is_running_tests() == True


def test_is_running_tests_returns_false_outside_test_execution_environment():
    # hacky, but has to be hacky for a test to assert something that by definition _can't_
    # occur while in the test execution environment

    manage_py_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "manage.py",
    )
    assert os.path.isfile(manage_py_path)

    # call is_running_tests in a sub-process, executed with manage.py shell
    non_test_execution_env_result = (
        os.popen(
            f'{manage_py_path} shell --command "from server.config_util import is_running_tests; print(is_running_tests())"'
        )
        .readlines()[-1]  #
        .strip()  # remove any leading spaces or tabs and trailing new lines
    )

    assert non_test_execution_env_result == "False"


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
