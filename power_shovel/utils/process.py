import os
import subprocess

from power_shovel import logger
from power_shovel.config import CONFIG
from power_shovel.exceptions import ExecuteFailed


def raise_for_status(code: int) -> None:
    """
    Raise `ExecuteFailed` if the code is an error code
    :param code: code to check
    """
    if code != 0:
        raise ExecuteFailed(f"Process returned a non-zero code: {code}")


def execute(command: str, silent: bool = False) -> int:
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
        print("logger: ", logger, logger.info)
        logger.info(formatted_command)

    # TODO: this was probable for compose. need a more dynamic way to handle adding env
    # env = os.environ.copy()
    # env["DOCKER_IMAGE"] = CONFIG.DOCKER.APP_IMAGE_FULL

    args = [arg for arg in formatted_command.split(" ") if arg]
    return subprocess.call(args)


def get_dev_uid():
    """get dev uid of running process"""
    return int(subprocess.check_output(["id", "-u"])[:-1])


def get_dev_gid():
    """get dev gid of running process"""
    return int(subprocess.check_output(["id", "-g"])[:-1])
