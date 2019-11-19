import os
from enum import Enum

import argcomplete
import argparse
import importlib
import importlib.machinery
import io
import types
import sys
from collections import defaultdict

from power_shovel import logger
from power_shovel.config import CONFIG
from power_shovel.logger import DEFAULT_LOG_LEVEL
from power_shovel.module import load_module
from power_shovel.utils import filesystem as file_utils
from power_shovel.exceptions import AlreadyComplete, ExecuteFailed
from power_shovel.task import TASKS, TaskRunner
from power_shovel.utils.color_codes import RED, ENDC
from power_shovel.utils.decorators import classproperty


class ExitCodes(Enum):
    """Codes that may be returned by cli"""

    SUCCESS = 0  # Success
    ERROR_COMPLETE = -1  # task is already complete
    ERROR_UNKNOWN_TASK = -2  # task isn't registered
    ERROR_NO_INIT = -3  # shovel.py does not contain an init flag
    ERROR_NO_SHOVEL_PY = -4  # shovel.py does not exist
    ERROR_TASK = -5  # task did not complete

    @classproperty
    def errors(cls):
        return [e for e in list(cls) if e.is_error]

    @classproperty
    def init_errors(cls):
        """Errors that init can raise"""
        return [
            cls.ERROR_NO_SHOVEL_PY,
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


def shovel_path() -> str:
    """Return path to shovel.py"""
    env_value = os.getenv("POWER_SHOVEL_CONFIG", None)
    if env_value:
        return env_value
    else:
        return f"{file_utils.pwd()}/shovel.py"


def import_shovel():
    """Imports a shovel module and returns it."""
    path = shovel_path()

    loader = importlib.machinery.SourceFileLoader("shovel", f"{path}")
    shovel_module = types.ModuleType(loader.name)
    loader.exec_module(shovel_module)
    return shovel_module


def init() -> ExitCodes:
    """init powershovel

    Finds the shovel config module for the projects and initializes itself
    using the `setup` function found inside shovel.py.

    :return:
    """
    init_logging()

    try:
        shovel_module = import_shovel()
    except FileNotFoundError as e:
        logger.error(str(e))
        return ExitCodes.ERROR_NO_SHOVEL_PY

    try:
        module_init = shovel_module.init
    except AttributeError:
        logger.error("init() was not found within shovel.py")
        return ExitCodes.ERROR_NO_INIT

    # init module and return all globals.
    logger.debug("Powershovel v0.0.1")
    load_module("power_shovel.modules.core")
    module_init()

    return ExitCodes.SUCCESS


def build_epilog() -> str:
    """Build help epilog text"""
    output = io.StringIO()
    if TASKS:
        categories = defaultdict(list)
        for task in TASKS.values():
            categories[task.category].append(task)
        padding = max(len(task.name) for task in TASKS.values())
        output.write(
            """Type 's2 help <subcommand>' for help on a specific """
            """subcommand.\n\n"""
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
    logger.set_level(args["log"])


def get_parser() -> argparse.ArgumentParser:
    """Return an instance of the base argument parser.

    The base parser has the internal flags but not tasks.
    :return: ArgumentParser that can parse args.
    """
    parser = argparse.ArgumentParser(
        prog="power_shovel",
        add_help=False,
        description="Run a power_shovel task.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=build_epilog(),
    )
    # TODO: try to fix formatting for choices
    parser.add_argument(
        "--help", help="show this help message and exit", action="store_true"
    )
    parser.add_argument(
        "--log",
        type=str,
        help="Log level (DEBUG|INFO|WARN|ERROR|NONE)",
        default=DEFAULT_LOG_LEVEL.name,
    )
    parser.add_argument("--force", help="force task execution", action="store_true")
    parser.add_argument(
        "--force-all",
        help="force execution including task dependencies",
        action="store_true",
    )
    parser.add_argument(
        "--clean", help="clean before running task", action="store_true"
    )
    parser.add_argument(
        "--clean-all",
        help="clean all dependencies before running task",
        action="store_true",
    )
    parser.add_argument(
        "remainder", nargs=argparse.REMAINDER, help="arguments for task."
    )
    return parser


DEFAULT_ARGS = {
    "clean": False,
    "clean_all": False,
    "force": False,
    "force_all": False,
    "log": logger.LogLevels.DEBUG,
    "task": "help",
    "task_args": None,
    "help": False,
}


def parse_args(args: str = None) -> dict:
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

    compiled_args["log"] = logger.LogLevels[compiled_args["log"]]

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

Type 's2 help <subcommand>' for help on a specific subcommand.
"""


def resolve_task(key: str) -> TaskRunner:
    """
    Resolve a task from the register by it's name

    :param key: name of task to resolve
    :return: TaskRunner instance
    """
    try:
        return TASKS[key]
    except KeyError:
        logger.error('Unknown task "%s", run with --help for list of commands' % key)


def run() -> ExitCodes:
    """
    Run power_shovel task

    :return: 0 if successful or an error code
    """

    # parse args
    args = parse_args()
    task_name = args.pop("task")
    task_args = args.pop("task_args")
    formatted_task_args = [CONFIG.format(arg) for arg in task_args]

    task = resolve_task(task_name)
    if not task:
        return ExitCodes.ERROR_UNKNOWN_TASK

    try:
        task.execute(formatted_task_args, **args)
    except AlreadyComplete:
        logger.warn("Already complete. Override with --force or --force-all")
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

    # run power_shovel
    run_code = run()
    if run_code is not None and run_code.is_error:
        exit_with_code(run_code)
    else:
        exit_with_code(ExitCodes.SUCCESS)
