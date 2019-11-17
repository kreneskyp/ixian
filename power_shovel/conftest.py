import pytest
from unittest import mock

from power_shovel.config import CONFIG
from power_shovel.exceptions import MockExit
from power_shovel.module import load_module, MODULES
from power_shovel.runner import ExitCodes
from power_shovel.task import TASKS
from power_shovel.test import fake

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
    mock_logger = mock.Mock()
    patchers = []

    for level in ["error", "warn", "info", "debug"]:
        patcher = mock.patch(f"power_shovel.logger.{level}")
        patchers.append(patcher)
        setattr(mock_logger, level, patcher.start())

    yield mock_logger

    for patcher in patchers:
        patcher.stop()


@pytest.fixture
def mock_environment():
    """
    Initialize power_shovel with a test environment
    """
    CONFIG.PROJECT_NAME = "unittests"
    load_module("power_shovel.modules.core")
    yield
    # Clear reference to runner else subsequent loads won't properly setup the tasks
    # TODO: this needs to be cleaned up when task loading is simplified
    for runner in TASKS.values():
        type(runner.task).__task__ = None
    TASKS.clear()
    MODULES.clear()


@pytest.fixture
def mock_init():
    """
    Mock `runner.init`
    """
    patcher = mock.patch("power_shovel.runner.init")
    mock_init = patcher.start()
    mock_init.return_value = ExitCodes.SUCCESS
    yield mock_init
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
    patcher = mock.patch("power_shovel.runner.run")
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
    patcher = mock.patch("power_shovel.runner.parse_args")
    mock_parse_args = patcher.start()
    mock_parse_args.return_value = fake.build_test_args()
    yield mock_parse_args
    patcher.stop()


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

    patcher = mock.patch("power_shovel.runner.sys.exit")
    mock_exit = patcher.start()
    mock_exit.side_effect = raise_exit_code
    yield mock_exit
    patcher.stop()
