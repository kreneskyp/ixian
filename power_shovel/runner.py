import argparse
import importlib
import io
import os
import sys

from collections import defaultdict

from power_shovel import logger
from power_shovel.module import load_module
from power_shovel.modules.filesystem import utils as file_utils
from power_shovel.task import AlreadyComplete
from power_shovel.utils.color_codes import RED, ENDC


def shovel_path():
    return file_utils.pwd() + '/shovel.py'


def import_shovel():
    """Imports a shovel module and returns it."""
    path = shovel_path()
    spec = importlib.util.spec_from_file_location('shovel', path)
    shovel_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(shovel_module)
    return shovel_module


def init():
    """init powershovel

    Finds the shovel config module for the projects and initializes itself
    using the `setup` function found inside shovel.py.

    :return:
    """
    init_logging()

    if not os.path.exists(shovel_path()):
        print ('shovel.py was not found in the current directory.')
        sys.exit(1)

    shovel_module = import_shovel()

    try:
        module_init = shovel_module.init
    except AttributeError:
        print('init() was not found within shovel.py')
        sys.exit(-1)

    # init module and return all globals.
    logger.debug('Powershovel v0.0.1')
    load_module('power_shovel.modules.core')
    module_init()
    from power_shovel.config import CONFIG
    from power_shovel.task import TASKS
    from power_shovel.module import MODULES

    return MODULES, TASKS, CONFIG


def build_epilog(tasks):
    output = io.StringIO()
    if tasks:
        categories = defaultdict(list)
        for task in tasks.values():
            categories[task.category].append(task)
        padding = max(len(task.name) for task in tasks.values())
        output.write("""Type 's2 help <subcommand>' for help on a specific """
                     """subcommand.\n\n""")
        output.write("""Available subcommands:\n\n""")

        for name, tasks in categories.items():
            output.write('{RED}[ {category} ]{ENDC}\n'.format(
                category=name.capitalize() if name else 'Misc',
                RED=RED,
                ENDC=ENDC,
            ))
            for task in sorted(tasks, key=lambda t: t.name.upper()):
                line ='  {task}    {help}\n'
                output.write(line.format(
                    task=task.name.ljust(padding, ' '),
                    help=task.short_description
                ))
            output.write('\n')

    return output.getvalue()


def init_logging():
    """Initialize logging system."""
    parser = get_parser({})
    args = parser.parse_args()
    log_level =  logger.LogLevels[args.log]
    logger.set_level(log_level)


def get_parser(tasks):
    """Return an instance of the base parser.

    The base parser has the internal flags but not tasks.
    :return:
    """
    parser = argparse.ArgumentParser(
        prog="power_shovel",
        description='Run a power_shovel task.',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=build_epilog(tasks))
    # TODO: try to fix formatting for choices
    parser.add_argument('--log',
                        type=str,
                        help='Log level (DEBUG|INFO|WARN|ERROR|NONE)',
                        default='DEBUG')
    parser.add_argument('--force',
                        help='force task execution',
                        action='store_true')
    parser.add_argument('--force-all',
                        help='force execution including task dependencies',
                        action='store_true')
    parser.add_argument('--clean',
                        help='clean before running task',
                        action='store_true')
    parser.add_argument('--clean-all',
                        help='clean all dependencies before running task',
                        action='store_true')
    parser.add_argument('task',
                        type=str,
                        default='help',
                        help='task to run')
    parser.add_argument('arg',
                        nargs=argparse.REMAINDER,
                        help='arguments for task.')
    return parser


def general_help(tasks):
    """General shovel help"""
    parser = get_parser(tasks)
    parser.print_help()


def run(modules, tasks, config):

    def resolve_task(key):
        # get command to run:
        #  - default to `help` task if no command specified.
        try:
            return tasks[key]
        except KeyError:
            print('Unknown task, run with --help for list of commands')
            sys.exit(-1)

    # parse args
    args = get_parser(tasks).parse_args()
    formatted_args = [config.format(arg) for arg in args.arg]

    # run help if help command given
    if args.task == 'help':
        if formatted_args and formatted_args[0]:
            task = resolve_task(formatted_args[0])
            task.render_help()
        else:
            general_help(tasks)
        sys.exit(0)

    # run task
    task = resolve_task(args.task)
    try:
        task.execute(
            formatted_args,
            clean=args.clean,
            clean_all=args.clean_all,
            force=args.force,
            force_all=args.force_all,
        )
    except AlreadyComplete:
        print('Already complete. Override with --force or --force-all')
