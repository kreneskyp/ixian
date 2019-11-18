import os
from unittest import mock

import pytest

from power_shovel import logger
from power_shovel import runner
from power_shovel.exceptions import MockExit
from power_shovel.runner import ExitCodes, shovel_path
from power_shovel.test.fake import build_test_args


def workspace(name: str) -> str:
    """
    Return the path to a shovel.py for a test workspace.
    :param name: name of workspace
    :return: path to shovel.py
    """
    import power_shovel.test.mocks as power_shovel_mocks

    base = os.path.dirname(os.path.realpath(power_shovel_mocks.__file__))
    return f"{base}/workspaces/{name}/shovel.py"


class TestExitCodes:
    def test_properties(self):
        ExitCodes.errors
        ExitCodes.init_errors
        ExitCodes.run_errors

    def test_is_success(self):
        assert ExitCodes.SUCCESS.is_success
        assert not ExitCodes.ERROR_COMPLETE.is_success
        assert not ExitCodes.ERROR_UNKNOWN_TASK.is_success
        assert not ExitCodes.ERROR_NO_INIT.is_success
        assert not ExitCodes.ERROR_NO_SHOVEL_PY.is_success
        assert not ExitCodes.ERROR_TASK.is_success

    def test_is_error(self):
        assert not ExitCodes.SUCCESS.is_error
        assert ExitCodes.ERROR_COMPLETE.is_error
        assert ExitCodes.ERROR_UNKNOWN_TASK.is_error
        assert ExitCodes.ERROR_NO_INIT.is_error
        assert ExitCodes.ERROR_NO_SHOVEL_PY.is_error
        assert ExitCodes.ERROR_TASK.is_error


class TestShovelPath:
    def test_default_shovel_path(self):
        # shovel.py is in the PWD by default if POWER_SHOVEL_CONFIG isn't set.
        assert shovel_path() == "/opt/power_shovel/shovel.py"

    def test_overridden_path(self):
        # config file path may be overridden by setting POWER_SHOVEL_CONFIG
        with mock.patch("power_shovel.runner.os.getenv", return_value="/tmp/config.py"):
            assert shovel_path() == "/tmp/config.py"


class TestInit:
    @mock.patch("power_shovel.runner.shovel_path")
    def test_no_shovel_py(self, shovel_path):
        """Test workspace without shovel.py"""
        shovel_path.return_value = workspace("missing_shovel_py")
        assert runner.init() == ExitCodes.ERROR_NO_SHOVEL_PY

    @mock.patch("power_shovel.runner.shovel_path")
    def test_no_init_method(self, shovel_path):
        """Test workspace with shovel.py, but module is missing init method"""
        shovel_path.return_value = workspace("shovel_py_no_init")
        assert runner.init() == ExitCodes.ERROR_NO_INIT

    @mock.patch("power_shovel.runner.shovel_path")
    def test_success(self, shovel_path):
        """Test a workspace that can be successfully loaded"""
        # TODO: this workspace should load tasks, need to clear registry after though
        shovel_path.return_value = workspace("functional")
        assert runner.init() == ExitCodes.SUCCESS


class TestLogging:
    def test_init_logging_default(self):
        # sanity check for exceptions
        runner.init_logging()

    @mock.patch("power_shovel.runner.parse_args")
    def test_log_level(self, parse_args):
        for level in logger.LogLevels:
            parse_args.return_value = build_test_args(log=level)
            runner.init_logging()
            logger.warn("warn")
            logger.info("info")
            logger.error("error")
            logger.debug("debug")


class TestParser:
    """
    Test that cli will parse args appropriately
    """

    def assertArgs(self, args, **extra):
        expected_args = build_test_args(**extra)
        parsed_args = runner.parse_args(args)
        assert parsed_args == expected_args

    def test_clean(self):
        self.assertArgs(["--clean", "foo"], task="foo", clean=True)

    def test_clean_all(self):
        self.assertArgs(["--clean-all", "foo"], task="foo", **{"clean_all": True})

    def test_force(self):
        self.assertArgs(["--force", "foo"], task="foo", force=True)

    def test_force_all(self):
        self.assertArgs(["--force-all", "foo"], task="foo", **{"force_all": True})

    def test_run(self):
        self.assertArgs(["foo"], task="foo")

    def test_unknown_task(self):
        self.assertArgs(["unknown_task"], task="unknown_task")

    def test_general_help(self):
        try:
            self.assertArgs(["--help"], task="help", help=True, task_args=[])
        except SystemExit as e:
            self.assertEqual(e.code, 0)
        try:
            self.assertArgs(["help"], task="help", task_args=[])
        except SystemExit as e:
            self.assertEqual(e.code, 0)

    def test_help_task(self):
        self.assertArgs(["help", "foo"], task="help", task_args=["foo"])

    def test_task_args(self):
        """
        Args that come after the task are passed to the task.

        A notable case is that --help before the task renders shovel help. --help after the task is
        passed to the task itself. This allows tasks to be a proxy to other shell commands.
        :return:
        """
        self.assertArgs(["foo", "--help"], task="foo", task_args=["--help"])
        self.assertArgs(["foo", "-h"], task="foo", task_args=["-h"])
        self.assertArgs(["foo", "help"], task="foo", task_args=["help"])
        self.assertArgs(["foo", "bar"], task="foo", task_args=["bar"])
        self.assertArgs(["foo", "bar", "xoo"], task="foo", task_args=["bar", "xoo"])
        self.assertArgs(
            ["foo", "bar", "--help"], task="foo", task_args=["bar", "--help"]
        )
        self.assertArgs(["foo", "bar", "-h"], task="foo", task_args=["bar", "-h"])


class TestRun:
    """
    Tests for runner.run()
    """

    def assertRan(self, mock_task_, mock_parse_args, **extra_args):
        # Mock task.execute since these tests are testing args passed to execute.
        mock_task_.__task__.execute = mock.Mock()

        # update args with test specific args
        args = build_test_args(**extra_args)
        task_args = args.get("task_args")
        mock_parse_args.return_value = args

        runner.run()
        mock_task_.__task__.execute.assert_called_with(task_args, **args)

    def test_clean(self, mock_task, mock_parse_args):
        self.assertRan(mock_task, mock_parse_args, task="mock_task", clean=True)

    def test_clean_all(self, mock_task, mock_parse_args):
        self.assertRan(
            mock_task, mock_parse_args, task="mock_task", **{"clean_all": True}
        )

    def test_force(self, mock_task, mock_parse_args):
        self.assertRan(mock_task, mock_parse_args, task="mock_task", force=True)

    def test_force_all(self, mock_task, mock_parse_args):
        self.assertRan(
            mock_task, mock_parse_args, task="mock_task", **{"force_all": True}
        )

    def test_run(self, mock_task, mock_parse_args):
        self.assertRan(mock_task, mock_parse_args, task="mock_task")

    def test_task_args(self, mock_task, mock_parse_args):
        self.assertRan(mock_task, mock_parse_args, task="mock_task", task_args=["-h"])

    def test_unknown_task(self, mock_environment, mock_parse_args):
        mock_parse_args.return_value = build_test_args(task="unknown_task")
        assert runner.run() == ExitCodes.ERROR_UNKNOWN_TASK


class TestCLI:
    def test_init_errors(self, mock_init_exit_errors, mock_exit):
        """
        If `init` returns an error code the process should exit with the same code.
        """
        with pytest.raises(MockExit) as exit_call:
            runner.cli()
        assert exit_call.value.code == mock_init_exit_errors.return_value

    def test_run_errors(self, mock_init, mock_run_exit_errors, mock_exit):
        """
        if `run` returns an error code the process should exit with the same code.
        """
        with pytest.raises(MockExit) as exit_call:
            runner.cli()
        assert exit_call.value.code == mock_run_exit_errors.return_value

    # TODO: mock_task should mock an environment
    def test_success(self, mock_task, mock_init, mock_parse_args, mock_exit):
        mock_parse_args.return_value = build_test_args(task="mock_task")

        with pytest.raises(MockExit) as exit_call:
            runner.cli()
        assert exit_call.value.code == ExitCodes.SUCCESS
        mock_task.mock.assert_called_with()
