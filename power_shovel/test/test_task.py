from io import StringIO
from unittest import mock

import pytest

from power_shovel.exceptions import AlreadyComplete, ExecuteFailed
from power_shovel.task import clear_task_registry, Task, TaskRunner


CALL = mock.call()
DEPENDENT_CALL = mock.call(**{"clean-all": False, "force-all": False})


class TestTask:
    def test_task(self, mock_task):
        """Test running a single task"""
        mock_task(1, 2)
        call = mock.call(1, 2)
        mock_task.mock.assert_has_calls([call])

    def test_run_dependency(self, mock_nested_tasks):
        """Test running dependant tasks"""
        root, child, grandchild = mock_nested_tasks.mock_tasks

        root()
        root.mock.assert_has_calls([CALL])
        child.mock.assert_has_calls([CALL])
        grandchild.mock.assert_has_calls([CALL])
        root.reset_task_mocks()

        child()
        root.mock.assert_has_calls([])
        child.mock.assert_has_calls([CALL])
        grandchild.mock.assert_has_calls([CALL])
        root.reset_task_mocks()

        child()
        root.mock.assert_has_calls([])
        child.mock.assert_has_calls([])
        grandchild.mock.assert_has_calls([CALL])

    def test_run_clean(self, mock_tasks_with_cleaners):
        """Test forcing clean of task"""
        root, child, grandchild = mock_tasks_with_cleaners.mock_tasks

        root(clean=True)
        root.__task__.clean.assert_has_calls([CALL])
        child.__task__.clean.assert_has_calls([])
        grandchild.__task__.clean.assert_has_calls([])
        root.mock.assert_has_calls([CALL])
        child.mock.assert_has_calls([])
        grandchild.mock.assert_has_calls([])
        root.reset_task_mocks()
        root.reset_task_clean_mocks()

        child(clean=True)
        root.__task__.clean.assert_has_calls([])
        child.__task__.clean.assert_has_calls([CALL])
        grandchild.__task__.clean.assert_has_calls([])
        root.mock.assert_has_calls([])
        child.mock.assert_has_calls([CALL])
        grandchild.mock.assert_has_calls([])
        root.reset_task_mocks()
        root.reset_task_clean_mocks()

        grandchild(clean=True)
        root.__task__.clean.assert_has_calls([])
        child.__task__.clean.assert_has_calls([])
        grandchild.__task__.clean.assert_has_calls([CALL])
        root.mock.assert_has_calls([])
        child.mock.assert_has_calls([])
        grandchild.mock.assert_has_calls([CALL])

    def test_run_clean_all(self, mock_tasks_with_cleaners):
        """Test forcing clean of entire dependency tree before run"""
        root, child, grandchild = mock_tasks_with_cleaners.mock_tasks

        root(clean_all=True)
        root.__task__.clean.assert_has_calls([CALL])
        child.__task__.clean.assert_has_calls([CALL])
        grandchild.__task__.clean.assert_has_calls([CALL])
        root.mock.assert_has_calls([CALL])
        child.mock.assert_has_calls([CALL])
        grandchild.mock.assert_has_calls([CALL])
        root.reset_task_mocks()
        root.reset_task_clean_mocks()

        child(clean_all=True)
        root.__task__.clean.assert_has_calls([])
        child.__task__.clean.assert_has_calls([CALL])
        grandchild.__task__.clean.assert_has_calls([CALL])
        root.mock.assert_has_calls([])
        child.mock.assert_has_calls([CALL])
        grandchild.mock.assert_has_calls([CALL])
        root.reset_task_mocks()
        root.reset_task_clean_mocks()

        grandchild(clean_all=True)
        root.__task__.clean.assert_has_calls([])
        child.__task__.clean.assert_has_calls([])
        grandchild.__task__.clean.assert_has_calls([CALL])
        root.mock.assert_has_calls([])
        child.mock.assert_has_calls([])
        grandchild.mock.assert_has_calls([CALL])

    def test_run_checker(self, mock_tasks_with_passing_checkers):
        """
        Test passing checkers - the checkers should raise AlreadyComplete and skip running
        """
        root, child, grandchild = mock_tasks_with_passing_checkers.mock_tasks

        root_checker = root.__task__.checkers[0]
        child_checker = child.__task__.checkers[0]
        grandchild_checker = grandchild.__task__.checkers[0]

        with pytest.raises(AlreadyComplete):
            root()

        root_checker.check.assert_has_calls([])
        child_checker.check.assert_has_calls([])
        grandchild_checker.check.assert_has_calls([])
        root.assert_no_calls()
        root.assert_no_checker_save_calls()
        root.reset_task_checkers_check()

        with pytest.raises(AlreadyComplete):
            child()
        root_checker.check.assert_has_calls([])
        child_checker.check.assert_has_calls([])
        grandchild_checker.check.assert_has_calls([])
        root.assert_no_calls()
        root.assert_no_checker_save_calls()
        root.reset_task_checkers_check()

        with pytest.raises(AlreadyComplete):
            grandchild()
        root_checker.check.assert_has_calls([])
        child_checker.check.assert_has_calls([])
        grandchild_checker.check.assert_has_calls([])
        root.assert_no_calls()
        root.assert_no_checker_save_calls()
        root.reset_task_checkers_check()

    def test_run_force(self, mock_tasks_with_passing_checkers):
        """Test forcing run of task"""
        root, child, grandchild = mock_tasks_with_passing_checkers.mock_tasks

        root_checker = root.__task__.checkers[0]
        child_checker = child.__task__.checkers[0]
        grandchild_checker = grandchild.__task__.checkers[0]

        root(force=True)
        root_checker.check.assert_has_calls([])
        child_checker.check.assert_has_calls([])
        grandchild_checker.check.assert_has_calls([])
        root.mock.assert_has_calls([CALL])
        child.mock.assert_has_calls([])
        grandchild.mock.assert_has_calls([])
        root.reset_task_checkers_check()

        child(force=True)
        root_checker.check.assert_has_calls([])
        child_checker.check.assert_has_calls([])
        grandchild_checker.check.assert_has_calls([])
        root.mock.assert_has_calls([])
        child.mock.assert_has_calls([CALL])
        grandchild.mock.assert_has_calls([])
        root.reset_task_checkers_check()

        grandchild(force=True)
        root_checker.check.assert_has_calls([])
        child_checker.check.assert_has_calls([])
        grandchild_checker.check.assert_has_calls([])
        root.mock.assert_has_calls([])
        child.mock.assert_has_calls([])
        grandchild.mock.assert_has_calls([CALL])
        root.reset_task_checkers_check()

    def test_run_force_all(self, mock_tasks_with_passing_checkers):
        """
        Test forcing run of entire dependency tree

        Checkers should be skipped since they are forced. all methods should run.
        """
        root, child, grandchild = mock_tasks_with_passing_checkers.mock_tasks

        root(force_all=True)
        root.assert_no_checker_calls()
        root.mock.assert_has_calls([CALL])
        child.mock.assert_has_calls([CALL])
        grandchild.mock.assert_has_calls([CALL])
        root.reset_task_checkers_check()

        child(force_all=True)
        root.assert_no_checker_calls()
        root.mock.assert_has_calls([])
        child.mock.assert_has_calls([CALL])
        grandchild.mock.assert_has_calls([CALL])
        root.reset_task_checkers_check()

        grandchild(force_all=True)
        root.assert_no_checker_calls()
        root.mock.assert_has_calls([])
        child.mock.assert_has_calls([])
        grandchild.mock.assert_has_calls([CALL])
        root.reset_task_checkers_check()

    def test_execute_failure(self, mock_tasks_that_fail):
        """
        If a task fails the execution chain should stop.
        :return:
        """
        root, child, grandchild = mock_tasks_that_fail.mock_tasks

        with pytest.raises(ExecuteFailed):
            grandchild()

        root.mock.assert_has_calls([])
        child.mock.assert_has_calls([])


class TestTaskTree:
    """
    Test task tree methods of TaskRunner
    """

    def test_tree(self, snapshot, mock_task_scenarios):
        runner = mock_task_scenarios.__task__
        tree = runner.tree(dedupe=False, flatten=False)
        snapshot.assert_match(tree)

    def test_tree_deduped(self, snapshot, mock_task_scenarios):
        runner = mock_task_scenarios.__task__
        tree = runner.tree(dedupe=True, flatten=False)
        snapshot.assert_match(tree)

    def test_tree_flattened(self, snapshot, mock_task_scenarios):
        runner = mock_task_scenarios.__task__
        tree = runner.tree(dedupe=True, flatten=True)
        snapshot.assert_match(tree)

    def test_status(self, snapshot, mock_task_scenarios):
        runner = mock_task_scenarios.__task__
        tree = runner.status(dedupe=False, flatten=False)
        snapshot.assert_match(tree)

    def test_status_deduped(self, snapshot, mock_task_scenarios):
        runner = mock_task_scenarios.__task__
        tree = runner.status(dedupe=True, flatten=False)
        snapshot.assert_match(tree)

    def test_status_flattened(self, snapshot, mock_task_scenarios):
        runner = mock_task_scenarios.__task__
        tree = runner.status(dedupe=True, flatten=True)
        snapshot.assert_match(tree)


class TestTaskHelp:
    def teardown_method(self):
        clear_task_registry()

    def test_render_help(self, snapshot):
        class MockTask(Task):
            """This is a mock test"""

            name = "mock_test"
            config = ["{POWER_SHOVEL}", "{PROJECT_NAME}"]

            def execute(self, *args, **kwargs):
                pass

        MockTask()
        output = StringIO()
        # Add an extra CR so snapshot is easier to read.
        output.write("\n")
        MockTask.__task__.render_help(output)
        snapshot.assert_match(output.getvalue())

    def test_render_help_no_docstring(self, snapshot):
        """
        Help should still render if task has no docstring. The docstring is the long description
        for the task.
        """

        class MockTask(Task):
            name = "mock_test"
            config = ["{POWER_SHOVEL}", "{PROJECT_NAME}"]

            def execute(self, *args, **kwargs):
                pass

        MockTask()
        output = StringIO()
        # Add an extra CR so snapshot is easier to read.
        output.write("\n")
        MockTask.__task__.render_help(output)
        snapshot.assert_match(output.getvalue())

    def test_render_help_no_config(self, snapshot):
        """
        Help should still render if config is missing. Config is a list of settings that are
        relevent to the Task. The settings key and value are rendered in the help to give users
        context
        """

        class MockTask(Task):
            """This is a mock test"""

            name = "mock_test"

            def execute(self, *args, **kwargs):
                pass

        MockTask()
        output = StringIO()
        # Add an extra CR so snapshot is easier to read.
        output.write("\n")
        MockTask.__task__.render_help(output)
        snapshot.assert_match(output.getvalue())

    def assert_render_status(self, snapshot, task_runner: TaskRunner) -> None:
        output = StringIO()
        # Add an extra CR so snapshot is easier to read.
        output.write("\n")
        runner = task_runner
        runner.render_status(output)
        snapshot.assert_match(output.getvalue())

    def test_render_status(self, snapshot, mock_task_scenarios):
        """
        Test rendering status for various task trees.
        """
        self.assert_render_status(snapshot, mock_task_scenarios.__task__)

    def test_render_status_passing_checks(
        self, snapshot, mock_tasks_with_passing_checkers
    ):
        # mock checkers for the tree and test when tree is passing
        self.assert_render_status(snapshot, mock_tasks_with_passing_checkers.__task__)
