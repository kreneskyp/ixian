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
import shutil

import pytest
from unittest import mock

from ixian.config import CONFIG
from ixian.exceptions import MockExit
from ixian.module import load_module, MODULES
from ixian.runner import ExitCodes
from ixian.task import TASKS
from ixian.tests import fake

# =================================================================================================
# Environment and system components
# =================================================================================================


@pytest.fixture
def mock_logger():
    """
    Mock the logging system.

    Modules usually import `logging` as a module. That import can't be mocked generically but the
    methods inside it can be. Mock the methods individually and return a single mock with them
    attached.
    """

    patcher = mock.patch(f"logging.getLogger")
    mock_logger = patcher.start()

    yield mock_logger

    patcher.stop()


@pytest.fixture
def mock_environment():
    """
    Initialize ixian with a tests environment
    """
    CONFIG.PROJECT_NAME = "unittests"
    CONFIG.LOGGING_CONFIG = {
        "version": 1,
        "formatters": {"stdout": {"class": "logging.Formatter", "format": "%(message)s",},},
        "handlers": {
            "stdout": {"class": "logging.StreamHandler", "formatter": "stdout", "level": "DEBUG",}
        },
        "root": {"level": "DEBUG", "handlers": ["stdout"]},
    }
    load_module("ixian.modules.core")
    yield
    # Clear reference to runner else subsequent loads won't properly setup the tasks
    # TODO: this needs to be cleaned up when task loading is simplified
    for runner in TASKS.values():
        if runner.task:
            type(runner.task).__task__ = None
    TASKS.clear()
    MODULES.clear()


@pytest.fixture
def mock_init():
    """
    Mock `runner.init`
    """
    patcher = mock.patch("ixian.runner.init")
    mock_init = patcher.start()
    mock_init.return_value = ExitCodes.SUCCESS
    yield mock_init
    patcher.stop()


@pytest.fixture
def mock_cli(mock_environment, mock_init):
    patcher = mock.patch("ixian.runner.sys")
    mock_sys = patcher.start()

    def mock_in(cmd):
        mock_sys.argv = ["mocked"] + cmd.split(" ")

    mock_sys.mock_in = mock_in
    yield mock_sys
    patcher.stop()


@pytest.fixture(params=ExitCodes.init_errors)
def mock_init_exit_errors(request, mock_init):
    mock_init.return_value = request.param
    yield mock_init


@pytest.fixture
def mock_run():
    """
    Mock `runner.run`
    """
    patcher = mock.patch("ixian.runner.run")
    mock_run = patcher.start()
    mock_run.return_value = ExitCodes.SUCCESS
    yield mock_run
    patcher.stop()


@pytest.fixture(params=ExitCodes.run_errors)
def mock_run_exit_errors(request, mock_run):
    mock_run.return_value = request.param
    yield mock_run


@pytest.fixture
def mock_parse_args():
    """
    Mock runner.parse_args()
    """
    patcher = mock.patch("ixian.runner.parse_args")
    mock_parse_args = patcher.start()
    mock_parse_args.return_value = fake.build_test_args()
    yield mock_parse_args
    patcher.stop()


@pytest.fixture
def temp_builder():
    """
    Fixture that creates a builder dir in /tmp and then removes it afterwards. Intended for use
    with tests that aren't mocking writes/reads from the builder cache.
    """
    CONFIG.BUILDER = "/tmp/.builder"
    if os.path.exists(CONFIG.BUILDER):
        shutil.rmtree(CONFIG.BUILDER)
    yield
    if os.path.exists(CONFIG.BUILDER):
        shutil.rmtree(CONFIG.BUILDER)


# =================================================================================================
# Tasks and trees of tasks
# =================================================================================================


@pytest.fixture
def mock_task(mock_environment):
    """Create a single mock task"""
    yield fake.mock_task()


@pytest.fixture
def mock_nested_tasks(mock_environment):
    """Create a single mock task"""
    yield fake.mock_nested_single_dependency_nodes()


@pytest.fixture
def mock_tasks_with_cleaners(mock_environment):
    """nested tasks all with mocked cleaner functions"""
    yield fake.mock_tasks_with_clean_functions()


@pytest.fixture
def mock_tasks_with_passing_checkers(mock_environment):
    """nested tasks all with mocked cleaner functions"""
    yield fake.mock_tasks_with_passing_checkers()


@pytest.fixture
def mock_tasks_with_failing_checkers(mock_environment):
    yield fake.mock_tasks_with_failing_checkers()


@pytest.fixture
def mock_tasks_that_fail(mock_environment):
    """nested tasks all with mocked cleaner functions"""
    yield fake.mock_failing_tasks()


@pytest.fixture(params=list(fake.MOCK_TASKS.keys()))
def mock_task_scenarios(request, mock_environment):
    """
    Fixture that iterates through all MOCK_TASKS scenarios
    """
    yield fake.MOCK_TASKS[request.param]()


# =================================================================================================
# Utils
# =================================================================================================


@pytest.fixture
def mock_exit():
    def raise_exit_code(code):
        raise MockExit(ExitCodes(code))

    patcher = mock.patch("ixian.runner.sys.exit")
    mock_exit = patcher.start()
    mock_exit.side_effect = raise_exit_code
    yield mock_exit
    patcher.stop()
