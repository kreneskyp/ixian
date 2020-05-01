# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from pysnap import Snapshot


snapshots = Snapshot()

snapshots['TestHelp.test_general_help 1'] = '''usage: ixian [--help] [--log LOG] [--force] [--force-all] [--clean]
             [--clean-all]
             ...

Run a ixian task.

positional arguments:
  remainder    arguments for task.

optional arguments:
  --help       show this help message and exit
  --log LOG    Log level (DEBUG|INFO|WARN|ERROR|NONE)
  --force      force task execution
  --force-all  force execution including task dependencies
  --clean      clean before running task
  --clean-all  clean all dependencies before running task

Type 'ix help <subcommand>' for help on a specific subcommand.

Available subcommands:

\x1b[91m[ Testing ]\x1b[0m
  lint     Run all linting tasks.
  test     Run all testing tasks.

\x1b[91m[ Build ]\x1b[0m
  clean    Run all clean tasks.

\x1b[91m[ Misc ]\x1b[0m
  help     This help message or help <task> for task help
'''

snapshots['TestHelp.test_task_help 1'] = '''\x1b[1mNAME
\x1b[0m    clean -- Run all clean tasks.
\x1b[1m
DESCRIPTION
\x1b[0mVirtual target for cleaning the project.\x1b[1m

STATUS
\x1b[0m\x1b[90m○\x1b[0m clean

'''

snapshots['TestHelp.test_task_help 2'] = ''
