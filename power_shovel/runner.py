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
                help='TODO HELP TEXT'
            ))
        output.write('\n')

    return output.getvalue()


def build_parser(tasks):
    parser = argparse.ArgumentParser(
        prog="power_shovel",
        description='Run a power_shovel task.',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=build_epilog(tasks))
    # TODO: try to fix formatting for choices
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
    parser.add_argument('task', type=str, default='help')
    parser.add_argument('arg', nargs=argparse.REMAINDER)
    return parser


def setup_logging(level):
    pass


def run():
    # initialize
    modules, tasks, config = init()

    # parse args
    args = build_parser(tasks).parse_args()

    # get command to run:
    #  - default to `help` task if no command specified.
    try:
        task = tasks[args.task]
    except KeyError:
        print('Unknown task, run with --help for list of commands')
        sys.exit(-1)

    setup_logging(args.log)

    # format all args with config
    formatted_args = [config.format(arg) for arg in args.arg]

    # run command
    task.execute(formatted_args, clean=args.clean, force=args.force)
