import argparse
import importlib
import io
import os
import sys

from collections import defaultdict


from power_shovel.modules.filesystem import utils as file_utils
from power_shovel.utils.color_codes import RED, ENDC


def shovel_path():
    return file_utils.pwd() + '/shovel.py'


def import_shovel():
    """Imports shovel module"""
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
    module_init()
    from power_shovel.config import CONFIG
    from power_shovel.task import TASKS
    from power_shovel.module import MODULES

    return MODULES, TASKS, CONFIG


def build_epilog(tasks):
    categories = defaultdict(list)
    for task in tasks.values():
        categories[task.category].append(task)
    padding = max(len(task.name) for task in tasks.values())

    output = io.StringIO()
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


def base_parser(tasks):
    """Return an instance of the base parser.

    The base parser has the internal flags but not tasks.
    :return:
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="power_shovel",
        description='Run a power_shovel task.',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=build_epilog(tasks))
    # TODO: try to fix formatting for choices
    parser.add_argument('--help',
                        help='Display this help or help for command',
                        action='store_true')
    parser.add_argument('--log',
                        type=str,
                        help='Log level (DEBUG|INFO|WARN|ERROR)',
                        default='DEBUG')
    parser.add_argument('--force',
                        help='force task execution',
                        action='store_true')
    parser.add_argument('--clean',
                        help='clean before running task',
                        action='store_true')
    return parser


def help_parser(tasks):
    """Parser for parsing just the help"""
    parser = base_parser(tasks)
    parser.add_argument('arg', nargs=argparse.REMAINDER)
    return parser


def task_parser(tasks):
    """Parser for parsing task execution"""
    parser = base_parser(tasks)
    parser.add_argument('task', type=str, default='help')
    parser.add_argument('arg', nargs=argparse.REMAINDER)
    return parser


def setup_logging(level):
    pass


def general_help(tasks):
    """General shovel help"""
    parser = task_parser(tasks)
    parser.print_help()


def run():
    # initialize
    modules, tasks, config = init()

    def resolve_task(key):
        # get command to run:
        #  - default to `help` task if no command specified.
        try:
            return tasks[key]
        except KeyError:
            print('Unknown task, run with --help for list of commands')
            sys.exit(-1)

    # parse args - the custom help handling means --help won't work without the
    # task as a positional arg. Use a separate parser to check help.
    if sys.argv:
        # Run help if --help is present.
        help_args = help_parser(tasks).parse_args()
        if help_args.help:
            if help_args.arg:
                task = resolve_task(help_args.arg[0])
                task.render_help()
            else:
                general_help(tasks)
            sys.exit(0)

        # parse args for regular task
        args = task_parser(tasks).parse_args()
    else:
        # still run task parser to trigger error handling message
        task_parser(tasks).parse_args()

    setup_logging(args.log)

    # format all args with config
    formatted_args = [config.format(arg) for arg in args.arg]

    # run task
    task = resolve_task(args.task)
    task.execute(formatted_args, clean=args.clean, force=args.force)
