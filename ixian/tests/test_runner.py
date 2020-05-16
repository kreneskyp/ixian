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

import os
from unittest import mock

import pytest

from ixian import runner
from ixian.exceptions import MockExit, AlreadyComplete, ExecuteFailed
from ixian.runner import ExitCodes, ixian_path
from ixian.tests.fake import build_test_args


def workspace(name: str) -> str:
    """
    Return the path to a ixian.py for a test workspace.
    :param name: name of workspace
    :return: path to ixian.py
    """
    import ixian.tests.mocks as ixian_mocks

    base = os.path.dirname(os.path.realpath(ixian_mocks.__file__))
    return f"{base}/workspaces/{name}/ixian.py"


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
        assert not ExitCodes.ERROR_NO_IXIAN_PY.is_success
        assert not ExitCodes.ERROR_TASK.is_success

    def test_is_error(self):
        assert not ExitCodes.SUCCESS.is_error
        assert ExitCodes.ERROR_COMPLETE.is_error
        assert ExitCodes.ERROR_UNKNOWN_TASK.is_error
        assert ExitCodes.ERROR_NO_INIT.is_error
        assert ExitCodes.ERROR_NO_IXIAN_PY.is_error
        assert ExitCodes.ERROR_TASK.is_error


class TestIxianPath:
    def test_default_ixian_path(self):
        # ixian.py is in the PWD by default if IXIAN_CONFIG isn't set.
        assert ixian_path() == "/home/runner/work/ixian/ixian/ixian.py"

    def test_overridden_path(self):
        # config file path may be overridden by setting IXIAN_CONFIG
        with mock.patch("ixian.runner.os.getenv", return_value="/tmp/config.py"):
            assert ixian_path() == "/tmp/config.py"


class TestInit:
    @mock.patch("ixian.runner.ixian_path")
    def test_no_ixian_py(self, ixian_path):
        """Test workspace without ixian.py"""
        ixian_path.return_value = workspace("missing_ixian_py")
        assert runner.init() == ExitCodes.ERROR_NO_IXIAN_PY

    @mock.patch("ixian.runner.ixian_path")
    def test_no_init_method(self, ixian_path):
        """Test workspace with ixian.py, but module is missing init method"""
        ixian_path.return_value = workspace("ixian_py_no_init")
        assert runner.init() == ExitCodes.ERROR_NO_INIT

    @mock.patch("ixian.runner.ixian_path")
    def test_success(self, ixian_path):
        """Test a workspace that can be successfully loaded"""
        # TODO: this workspace should load tasks, need to clear registry after though
        ixian_path.return_value = workspace("functional")
        assert runner.init() == ExitCodes.SUCCESS


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
        self.assertArgs(["--help", "foo"], help=True, task="help", task_args=["foo"])

    def test_task_args(self):
        """
        Args that come after the task are passed to the task.

        A notable case is that --help before the task renders ixian help. --help after the task is
        passed to the task itself. This allows tasks to be a proxy to other shell commands.
        :return:
        """
        self.assertArgs(["foo", "--help"], task="foo", task_args=["--help"])
        self.assertArgs(["foo", "-h"], task="foo", task_args=["-h"])
        self.assertArgs(["foo", "help"], task="foo", task_args=["help"])
        self.assertArgs(["foo", "bar"], task="foo", task_args=["bar"])
        self.assertArgs(["foo", "bar", "xoo"], task="foo", task_args=["bar", "xoo"])
        self.assertArgs(["foo", "bar", "--help"], task="foo", task_args=["bar", "--help"])
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
        self.assertRan(mock_task, mock_parse_args, task="mock_task", **{"clean_all": True})

    def test_force(self, mock_task, mock_parse_args):
        self.assertRan(mock_task, mock_parse_args, task="mock_task", force=True)

    def test_force_all(self, mock_task, mock_parse_args):
        self.assertRan(mock_task, mock_parse_args, task="mock_task", **{"force_all": True})

    def test_run(self, mock_task, mock_parse_args):
        self.assertRan(mock_task, mock_parse_args, task="mock_task")

    def test_task_args(self, mock_task, mock_parse_args):
        self.assertRan(mock_task, mock_parse_args, task="mock_task", task_args=["-h"])

    def test_unknown_task(self, mock_environment, mock_parse_args):
        mock_parse_args.return_value = build_test_args(task="unknown_task")
        assert runner.run() == ExitCodes.ERROR_UNKNOWN_TASK

    def test_already_complete(self, mock_task, mock_parse_args):
        mock_parse_args.return_value = build_test_args(task="mock_task")
        mock_task.mock.side_effect = AlreadyComplete
        assert runner.run() == ExitCodes.ERROR_COMPLETE

    def test_execute_failed(self, mock_task, mock_parse_args):
        mock_parse_args.return_value = build_test_args(task="mock_task")
        mock_task.mock.side_effect = ExecuteFailed
        assert runner.run() == ExitCodes.ERROR_TASK


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
