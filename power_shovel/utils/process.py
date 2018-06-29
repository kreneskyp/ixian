import logging
import subprocess

from power_shovel import logger
from power_shovel.config import CONFIG


def execute(command, silent=False):
    """Execute a shell command"""
    formatted_command = CONFIG.format(command)
    if not silent:
        logger.info(formatted_command)

    args = [arg for arg in formatted_command.split(' ') if arg]
    return subprocess.call(args)


def get_dev_uid():
    """get dev uid of running process"""
    return subprocess.check_output(['id', '-u'])[:-1]


def get_dev_gid():
    """get dev gid of running process"""
    return subprocess.check_output(['id', '-g'])[:-1]
