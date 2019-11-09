import pytest

from power_shovel.task import clear_task_registry
from power_shovel.test.fake import (
    mock_task,
    mock_nested_single_dependency_nodes,
    MOCK_TASKS,
    mock_tasks_with_clean_functions,
    mock_tasks_with_passing_checkers,
    mock_failing_tasks,
)


@pytest.fixture()
def task(request):
    """Create a single mock task"""
    yield mock_task()
    clear_task_registry()


@pytest.fixture()
def nested_tasks(request):
    """Create a single mock task"""
    yield mock_nested_single_dependency_nodes()
    clear_task_registry()


@pytest.fixture()
def tasks_with_cleaners(request):
    """nested tasks all with mocked cleaner functions"""
    yield mock_tasks_with_clean_functions()
    clear_task_registry()


@pytest.fixture()
def tasks_with_passing_checkers(request):
    """nested tasks all with mocked cleaner functions"""
    yield mock_tasks_with_passing_checkers()
    clear_task_registry()


@pytest.fixture()
def tasks_that_fail(request):
    """nested tasks all with mocked cleaner functions"""
    yield mock_failing_tasks()
    clear_task_registry()


@pytest.fixture(params=list(MOCK_TASKS.keys()))
def task_scenarios(request):
    """
    Fixture that iterates through all MOCK_TASKS scenarios
    """
    yield MOCK_TASKS[request.param]()
    clear_task_registry()
