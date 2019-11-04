import pytest

from power_shovel.task import clear_task_registry
from power_shovel.test.fake import MOCK_TASKS


@pytest.fixture(params=list(MOCK_TASKS.keys()))
def task_scenarios(request):
    """
    Fixture that iterates through all MOCK_TASKS scenarios
    """
    yield MOCK_TASKS[request.param]()
    clear_task_registry()
