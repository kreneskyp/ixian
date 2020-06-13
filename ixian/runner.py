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
from enum import Enum
from logging.config import dictConfig
from typing import List

import argcomplete
import argparse
import importlib
import importlib.machinery
import io
import types
import sys
from collections import defaultdict

from ixian.config import CONFIG
from ixian.module import load_module
from ixian.utils import filesystem as file_utils
from ixian.exceptions import AlreadyComplete, ExecuteFailed
from ixian.task import TASKS, TaskRunner
from ixian.utils.color_codes import RED, ENDC
from ixian.utils.decorators import classproperty


logger = logging.getLogger(__name__)


class ExitCodes(Enum):
    """Codes that may be returned by cli"""

    SUCCESS = 0  # Success
    ERROR_COMPLETE = -1  # task is already complete
    ERROR_UNKNOWN_TASK = -2  # task isn't registered
    ERROR_NO_INIT = -3  # ixian.py does not contain an init flag
    ERROR_NO_IXIAN_PY = -4  # ixian.py does not exist
    ERROR_TASK = -5  # task did not complete

    @classproperty
    def errors(cls):
        return [e for e in list(cls) if e.is_error]

    @classproperty
    def init_errors(cls):
        """Errors that init can raise"""
        return [
            cls.ERROR_NO_IXIAN_PY,
            cls.ERROR_NO_INIT,
        ]

    @classproperty
    def run_errors(cls):
        """Errors that run can raise"""
        return [
            cls.ERROR_UNKNOWN_TASK,
            cls.ERROR_COMPLETE,
            cls.ERROR_TASK,
        ]

    @property
    def is_success(self):
        return self == self.SUCCESS

    @property
    def is_error(self):
        return self != self.SUCCESS


def ixian_path() -> str:
    """Return path to ixian.py"""
    env_value = os.getenv("IXIAN_CONFIG", None)
    if env_value:
        return env_value
    else:
        return f"{file_utils.pwd()}/ixian.py"


def import_ixian():
    """Imports a ixian module and returns it."""
    path = ixian_path()

    loader = importlib.machinery.SourceFileLoader("ixian", f"{path}")
    ixian_module = types.ModuleType(loader.name)
    loader.exec_module(ixian_module)
    return ixian_module


def init() -> ExitCodes:
    """init ixian

    Finds the ixian config module for the projects and initializes itself
    using the `setup` function found inside ixian.py.

    :return:
    """
    init_logging()

    try:
        ixian_module = import_ixian()
    except FileNotFoundError as e:
        logger.error(str(e))
        return ExitCodes.ERROR_NO_IXIAN_PY

    try:
        module_init = ixian_module.init
    except AttributeError:
        logger.error("init() was not found within ixian.py")
        return ExitCodes.ERROR_NO_INIT

    # init module and return all globals.
    logger.debug("Ixian v0.0.1")
    load_module("ixian.modules.core")
    module_init()

    return ExitCodes.SUCCESS


def build_epilog() -> str:
    """Build help epilog text"""
    output = io.StringIO()
    if TASKS:
        categories = defaultdict(list)
        for task in TASKS.values():
            # only list tasks for the current context
            if task.in_context:
                categories[task.category].append(task)
        padding = max(len(task.name) for task in TASKS.values())
        output.write(
            """Type 'ix help <subcommand>' for help on a specific """ """subcommand.\n\n"""
        )
        output.write("""Available subcommands:\n\n""")

        for name, tasks in categories.items():
            category = name.capitalize() if name else "Misc"
            output.write(f"{RED}[ {category} ]{ENDC}\n")
            for task in sorted(tasks, key=lambda t: t.name.upper()):
                task_name = task.name.ljust(padding, " ")
                output.write(f"  {task_name}    {task.short_description}\n")
            output.write("\n")

    return output.getvalue()


def init_logging() -> None:
    """Initialize logging system."""
    args = parse_args()

    dictConfig(CONFIG.LOGGING_CONFIG)
    root = logging.getLogger()
    root.setLevel(args["log"])


def get_parser() -> argparse.ArgumentParser:
    """Return an instance of the base argument parser.

    The base parser has the internal flags but not tasks.
    :return: ArgumentParser that can parse args.
    """
    parser = argparse.ArgumentParser(
        prog="ixian",
        add_help=False,
        description="Run a ixian task.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=build_epilog(),
    )
    # TODO: try to fix formatting for choices
    parser.add_argument("--help", help="show this help message and exit", action="store_true")
    parser.add_argument(
        "--log", type=str, help="Log level (DEBUG|INFO|WARN|ERROR|NONE)", default="DEBUG",
    )
    parser.add_argument("--force", help="force task execution", action="store_true")
    parser.add_argument(
        "--force-all", help="force execution including task dependencies", action="store_true",
    )
    parser.add_argument("--clean", help="clean before running task", action="store_true")
    parser.add_argument(
        "--clean-all", help="clean all dependencies before running task", action="store_true",
    )
    parser.add_argument("remainder", nargs=argparse.REMAINDER, help="arguments for task.")
    return parser


DEFAULT_ARGS = {
    "clean": False,
    "clean_all": False,
    "force": False,
    "force_all": False,
    "log": "DEBUG",
    "task": "help",
    "task_args": None,
    "help": False,
}


def parse_args(args: List[str] = None) -> dict:
    """Parse args from command line input"""
    parser = get_parser()
    compiled_args = DEFAULT_ARGS.copy()
    parsed_args, _ = parser.parse_known_args(args)
    compiled_args.update(parsed_args.__dict__)
    remainder = compiled_args.pop("remainder")

    if remainder:
        compiled_args["task"] = remainder[0]
        compiled_args["task_args"] = remainder[1:]
    else:
        compiled_args["task"] = "help"
        compiled_args["task_args"] = []

    compiled_args["log"] = compiled_args["log"]

    # if --help flag is given then run the "help" task. "--help <task>" and "help <task>" should
    # be treated the same.
    if parsed_args.help:
        # When --help is used the first arg is the task to show help for. The parser always saves
        # the first arg as "task". --help should always run "help" as the task. Move the task
        # into `task_args` so it is passed to the help task.
        if compiled_args["task"] and compiled_args["task"] != "help":
            compiled_args["task_args"] = [compiled_args["task"]]
        compiled_args["task"] = "help"

    return compiled_args


"""
optional arguments:
  -h, --help   show this help message and exit
  --log LOG    Log level (DEBUG|INFO|WARN|ERROR|NONE)
  --force      force task execution
  --force-all  force execution including task dependencies
  --clean      clean before running task
  --clean-all  clean all dependencies before running task

Type ix help <subcommand>' for help on a specific subcommand.
"""


# TODO: logging isn't working in this task
def resolve_task(key: str) -> TaskRunner:
    """
    Resolve a task from the register by it's name

    :param key: name of task to resolve
    :return: TaskRunner instance
    """
    try:
        task = TASKS[key]
    except KeyError:
        logger.error('Unknown task "%s", run with --help for list of commands' % key)
    else:
        if task.in_context:
            return task
        else:
            logger.debug(
                f"RUN_CONTEXT ({CONFIG.RUN_CONTEXT}) does not match task config"
                f"({task.task.contexts})"
            )


def load_environment():
    """
    Loads environment variables and updates CONFIG with them.
    """
    for key, value in os.environ.items():
        if key.startswith(CONFIG.ENV_PREFIX):
            parts = key[len(CONFIG.ENV_PREFIX) :].split("__")  # noqa: E203
            current = CONFIG
            for part in parts[:-1]:
                current = getattr(current, part)
            setattr(current, parts[-1], value)


def run() -> ExitCodes:
    """
    Run ixian task

    :return: 0 if successful or an error code
    """

    # parse args - manually grab from sys.argv so mock_cli can mock it.
    args = parse_args(sys.argv[1:])
    task_name = args.pop("task")
    task_args = args.pop("task_args")
    formatted_task_args = [CONFIG.format(arg) for arg in task_args]

    # TODO: load environment here for now. Eventually move this into init() so env is available
    #       as modules load. Dynamic loading like that is more complex
    load_environment()

    task = resolve_task(task_name)
    if not task:
        return ExitCodes.ERROR_UNKNOWN_TASK

    try:
        task.execute(formatted_task_args, **args)
    except AlreadyComplete:
        logger.warning("Already complete. Override with --force or --force-all")
        return ExitCodes.ERROR_COMPLETE
    except ExecuteFailed as e:
        logger.error(str(e))
        return ExitCodes.ERROR_TASK

    return ExitCodes.SUCCESS


def exit_with_code(code):
    if isinstance(code, ExitCodes):
        code = code.value
    sys.exit(code)


def cli() -> None:
    """
    Main entry point into the command line interface.
    """
    init_code = init()
    if init_code.is_error:
        exit_with_code(init_code)

    # setup autocomplete
    parser = get_parser()
    argcomplete.autocomplete(parser)

    # run ixian
    run_code = run()
    if run_code is not None and run_code.is_error:
        exit_with_code(run_code)
    else:
        exit_with_code(ExitCodes.SUCCESS)
