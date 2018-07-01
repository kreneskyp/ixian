import os
from unittest import TestCase
from unittest import mock

from power_shovel import logger
from power_shovel import runner
from power_shovel.task import TaskRunner
from power_shovel.task import TASKS
from power_shovel.config import CONFIG
from power_shovel.module import load_modules
from power_shovel.module import MODULES


def reset():
    """Reset environment."""
    TASKS.clear()
    MODULES.clear()


def init_test():
    """Initialize with test config"""
    CONFIG.PROJECT_NAME = 'unittests'
    load_modules(
        'power_shovel.modules.core',
        'power_shovel.test.modules.test'
    )


def init_failure_unknown_module():
    """Initialize with intentional error: unknown module"""
    load_modules('power_shovel.modules.unknown')


def workspace(path):
    import power_shovel.test as power_shovel_test
    base = os.path.dirname(os.path.realpath(power_shovel_test.__file__))
    return '{}/workspaces/{}'.format(base, path)


def build_test_args(**extra):
    args = runner.DEFAULT_ARGS.copy()
    args['task_args'] = []
    args.update(extra)
    return args


class InitTests(TestCase):

    @mock.patch('power_shovel.runner.shovel_path')
    def test_no_shovel_py(self, shovel_path):
        shovel_path.return_value = workspace('missing_shovel_py')
        self.assertEqual(runner.init(), runner.ERROR_NO_SHOVEL_PY)

    @mock.patch('power_shovel.runner.shovel_path')
    def test_no_init_method(self, shovel_path):
        shovel_path.return_value = workspace('shovel_py_no_init')
        self.assertEqual(runner.init(), runner.ERROR_NO_INIT)

    @mock.patch('power_shovel.runner.shovel_path')
    def test_success(self, shovel_path):
        shovel_path.return_value = workspace('functional')
        print(shovel_path.return_value)
        runner.init()


class LoggingTests(TestCase):

    def test_init_logging_default(self):
        # sanity check for exceptions
        runner.init_logging()

    @mock.patch('power_shovel.runner.parse_args')
    def test_log_level(self, parse_args):
        for level in logger.LogLevels:
            parse_args.return_value = build_test_args(log=level)
            runner.init_logging()
            logger.warn('warn')
            logger.info('info')
            logger.error('error')
            logger.debug('debug')


class InitedTest():
    """Testcases that start with the test config initialized."""

    def setUp(self):
        init_test()

    def teardown(self):
        reset()


class ParserTests(InitedTest, TestCase):

    def assertArgs(self, args, **extra):
        expected_args = build_test_args(**extra)
        parsed_args = runner.parse_args(args)
        self.assertEqual(parsed_args, expected_args)

    def test_clean(self):
        self.assertArgs(['--clean', 'foo'], task='foo', clean=True)

    def test_clean_all(self):
        self.assertArgs(['--clean-all', 'foo'],
                        task='foo', **{'clean_all': True})

    def test_force(self):
        self.assertArgs(['--force', 'foo'], task='foo', force=True)

    def test_force_all(self):
        self.assertArgs(['--force-all', 'foo'],
                        task='foo', **{'force_all': True})

    def test_run(self):
        self.assertArgs(['foo'], task='foo')

    def test_unknown_task(self):
        self.assertArgs(['unknown_task'], task='unknown_task')

    def test_general_help(self):
        try:
            self.assertArgs(['--help'], task='help', help=True, task_args=[])
        except SystemExit as e:
            self.assertEqual(e.code, 0)
        try:
            self.assertArgs(['help'], task='help', task_args=[])
        except SystemExit as e:
            self.assertEqual(e.code, 0)

    def test_help_task(self):
        self.assertArgs(['help', 'foo'], task='help', task_args=['foo'])

    def test_task_args(self):
        self.assertArgs(['foo', '--help'], task='foo', task_args=['--help'])
        self.assertArgs(['foo', '-h'], task='foo', task_args=['-h'])
        self.assertArgs(['foo', 'help'], task='foo', task_args=['help'])
        self.assertArgs(['foo', 'bar'], task='foo', task_args=['bar'])
        self.assertArgs(
            ['foo', 'bar', 'xoo'], task='foo', task_args=['bar', 'xoo'])
        self.assertArgs(
            ['foo', 'bar', '--help'], task='foo', task_args=['bar', '--help'])
        self.assertArgs(
            ['foo', 'bar', '-h'], task='foo', task_args=['bar', '-h'])


class RunTests(TestCase):

    def mock_parse_args(self, **extra_args):
        self.mock_parse_args = mock.patch('power_shovel.runner.parse_args')
        self.addCleanup(self.mock_parse_args.stop)
        self.parse_args = self.mock_parse_args.start()
        args = build_test_args(**extra_args)
        self.parse_args.return_value = args

    def setupRun(self, **extra_args):
        self.mock_parse_args(**extra_args)
        self.task = mock.MagicMock()
        self.task.__name__ = 'mock_task'
        self.mock_resolve_task = mock.patch('power_shovel.runner.resolve_task')
        self.addCleanup(self.mock_resolve_task.stop)
        self.resolve_task = self.mock_resolve_task.start()
        self.resolve_task.return_value = self.task

    def assertRan(self, **extra_args):
        self.setupRun(**extra_args)
        init_test()
        runner.run()

        args = build_test_args(**extra_args)
        del args['task']
        task_args = args.pop('task_args')
        self.task.execute.assert_called_with(
            task_args, **args
        )

    def tearDown(self):
        reset()

    def test_clean(self):
        self.assertRan(task='foo', clean=True)

    def test_clean_all(self):
        self.assertRan(task='foo', **{'clean_all': True})

    def test_force(self):
        self.assertRan(task='foo', force=True)

    def test_force_all(self):
        self.assertRan(task='foo', **{'force_all': True})

    def test_run(self):
        self.assertRan(task='foo')

    def test_general_help(self):
        self.assertRan(task='help')

    def test_help_task(self):
        self.assertRan(task='help', task_args=['foo'])

    def test_task_args(self):
        self.assertRan(task='foo', task_args=['-h'])

    def test_unknown_task(self):
        self.mock_parse_args(task='unknown_task')
        self.assertEqual(-2, runner.run())



