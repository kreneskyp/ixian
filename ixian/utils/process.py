# Copyright [2018-2020] Peter Krenesky
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import subprocess

from ixian.config import CONFIG
from ixian.exceptions import ExecuteFailed


logger = logging.getLogger(__name__)


def raise_for_status(code: int) -> None:
    """
    Raise `ExecuteFailed` if the code is an error code
    :param code: code to check
    """
    if code != 0:
        raise ExecuteFailed(f"Process returned a non-zero code: {code}")


def execute(command: str, silent: bool = False, env: dict = None) -> int:
    """
    Execute a shell command.

    ```
    execute("echo this is an example")
    ```

    Any config variables will be expanded.

    ```
    execute("echo this is the working directory: {PWD}")
    ```

    :param command: space separated command and args
    :param silent: do not echo command
    :return:
    """
    formatted_command = CONFIG.format(command)
    if not silent:
        logger.info(formatted_command)

    # Need to pass full environment, merge passed in env with process env.
    built_env = os.environ.copy()
    if env:
        built_env.update(env)

    args = [arg for arg in formatted_command.split(" ") if arg]
    return subprocess.call(args, env=built_env)


def get_dev_uid() -> int:
    """get dev uid of running process"""
    return int(subprocess.check_output(["id", "-u"])[:-1])


def get_dev_gid() -> int:
    """get dev gid of running process"""
    return int(subprocess.check_output(["id", "-g"])[:-1])
