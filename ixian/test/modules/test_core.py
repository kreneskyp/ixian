import pytest

from ixian.config import CONFIG
from ixian.module import MODULES
from ixian.runner import resolve_task
from ixian.task import TASKS


def test_load(mock_environment):
    # CORE is loaded by mock_environment
    from ixian.modules.core import OPTIONS
    from ixian.modules.core import tasks
    from ixian.config import Config

    # all tasks are loaded
    assert resolve_task("help") is tasks.Help.__task__
    assert resolve_task("clean") is tasks.Clean.__task__
    assert resolve_task("lint") is tasks.Lint.__task__
    assert resolve_task("test") is tasks.Test.__task__

    # verify options and config loaded
    assert "CORE" in MODULES
    assert MODULES["CORE"] == OPTIONS
    assert type(CONFIG) == Config


@pytest.mark.usefixtures("mock_environment")
class TestHelp:
    def test_general_help(self, snapshot, capsys):
        # general help is shown when no args are passed to task
        help = resolve_task("help")
        assert help() == 0
        out, err = capsys.readouterr()
        snapshot.assert_match(out)

    def test_task_help(self, snapshot, capsys):
        # task specific help is rendered if a task_name is given
        help = resolve_task("help")
        assert help("clean") == 0
        out, err = capsys.readouterr()
        snapshot.assert_match(out)
        snapshot.assert_match(err)
