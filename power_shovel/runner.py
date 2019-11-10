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
from power_shovel.modules.filesystem import utils as file_utils
from power_shovel.task import AlreadyComplete
from power_shovel.task import TASKS
from power_shovel.utils.color_codes import RED, ENDC

# Runner process error exit codes
ERROR_COMPLETE = -1  # task is already complete
ERROR_UNKNOWN_TASK = -2  # task isn't registered
ERROR_NO_INIT = -3  # shovel.py does not contain an init flag
ERROR_NO_SHOVEL_PY = -4  # shovel.py does not exist
ERROR_TASK = -5  # task did not complete


def shovel_path() -> str:
    """Return path to shovel.py"""
    return f"{file_utils.pwd()}/shovel.py"


def import_shovel():
    """Imports a shovel module and returns it."""
    path = shovel_path()

    loader = importlib.machinery.SourceFileLoader("shovel", f"{path}")
    shovel_module = types.ModuleType(loader.name)
    loader.exec_module(shovel_module)
    return shovel_module


def init() -> int:
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
        return ERROR_NO_SHOVEL_PY

    try:
        module_init = shovel_module.init
    except AttributeError:
        logger.error("init() was not found within shovel.py")
        return ERROR_NO_INIT

    # init module and return all globals.
    logger.debug("Powershovel v0.0.1")
    load_module("power_shovel.modules.core")
    module_init()

    return 0


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

    # if --help flag is given then run that task.
    if parsed_args.help:
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


def run() -> int:
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
        return ERROR_UNKNOWN_TASK

    try:
        task.execute(formatted_task_args, **args)
    except AlreadyComplete:
        logger.warn("Already complete. Override with --force or --force-all")
        return ERROR_COMPLETE
    except ExecuteFailed as e:
        logger.error(str(e))
        return ERROR_TASK

    return 0


def cli() -> None:
    """
    Main entry point into the command line interface.
    """
    init_code = init()
    if init_code < 0:
        sys.exit(init_code)

    # setup autocomplete
    parser = get_parser()
    argcomplete.autocomplete(parser)

    # run power_shovel
    run_code = run()
    if run_code is not None and run_code < 0:
        sys.exit(run_code)
    else:
        sys.exit(0)
