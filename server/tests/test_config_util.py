import os
import subprocess
import sys
from unittest import mock

import pytest
from decouple import UndefinedValueError

from server.config_util import (
    DEV_PUBLIC_ENV_FILE_NAME,
    DEV_SECRET_ENV_FILE_NAME,
    K8S_FLAG_ENV_VAR_KEY,
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
    subprocess.run(
        [
            "python",
            manage_py_path,
            "shell",
            "--command",
            "from server.config_util import is_running_tests; print(f'is_running_tests: {is_running_tests()}'); assert not is_running_tests()",
        ],
        check=True,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )


@mock.patch.dict(os.environ, {K8S_FLAG_ENV_VAR_KEY: "true"})
def test_get_project_config_ignoes_env_files_if_k8s(tmp_path):
    write_env_file(tmp_path, DEV_PUBLIC_ENV_FILE_NAME)
    write_env_file(tmp_path, DEV_SECRET_ENV_FILE_NAME)

    config = get_project_config(env_dir=tmp_path)

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
