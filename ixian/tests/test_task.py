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

from io import StringIO
from unittest import mock

import pytest

from ixian.exceptions import AlreadyComplete, ExecuteFailed
from ixian.task import Task, TaskRunner, VirtualTarget, TASKS
from ixian.tests import fake
from ixian.tests.mock_checker import FailingCheck, PassingCheck

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
        root, child, grandchild = mock_nested_tasks.mock_tasks.values()

        root()
        root.assert_all_tasks_ran()
        root.reset_mocks()

        child()
        root.assert_tasks_ran(child=True, grandchild=True)
        root.reset_mocks()

        grandchild()
        root.assert_tasks_ran(grandchild=True)

    def test_run_clean(self, mock_tasks_with_cleaners):
        """Test forcing clean of task"""
        root, child, grandchild = mock_tasks_with_cleaners.mock_tasks.values()

        root(clean=True)
        root.assert_all_tasks_ran()
        root.assert_cleaners_ran(root=True)
        root.reset_mocks()

        child(clean=True)
        root.assert_tasks_ran(child=True, grandchild=True)
        root.assert_cleaners_ran(child=True)
        root.reset_mocks()

        grandchild(clean=True)
        root.assert_tasks_ran(grandchild=True)
        root.assert_cleaners_ran(grandchild=True)

    def test_run_clean_all(self, mock_tasks_with_cleaners):
        """Test forcing clean of entire dependency tree before run"""
        root, child, grandchild = mock_tasks_with_cleaners.mock_tasks.values()

        root(clean_all=True)
        root.assert_all_cleaners_ran()
        root.assert_all_tasks_ran()
        root.reset_mocks()
        root.assert_cleaners_ran()

        child(clean_all=True)
        root.assert_cleaners_ran(child=True, grandchild=True)
        root.assert_tasks_ran(child=True, grandchild=True)
        root.reset_mocks()

        grandchild(clean_all=True)
        root.assert_cleaners_ran(grandchild=True)
        root.assert_tasks_ran(grandchild=True)
        root.reset_mocks()

    def test_run_checkers_already_complete(self, mock_tasks_with_passing_checkers):
        """
        Test passing checkers - the checkers should raise AlreadyComplete and skip running.
        """
        root, child, grandchild = mock_tasks_with_passing_checkers.mock_tasks.values()

        with pytest.raises(AlreadyComplete):
            root()

        root.assert_no_calls()
        root.assert_all_checkers_ran()
        root.assert_no_checkers_saved()
        root.reset_mocks()

        with pytest.raises(AlreadyComplete):
            child()
        root.assert_no_calls()
        root.assert_checkers_ran(child=True, grandchild=True)
        root.assert_no_checkers_saved()
        root.reset_mocks()

        with pytest.raises(AlreadyComplete):
            grandchild()
        root.assert_no_calls()
        root.assert_checkers_ran(grandchild=True)
        root.assert_no_checkers_saved()
        root.reset_mocks()

    def test_run_checkers_not_complete(self, mock_tasks_with_failing_checkers):
        """
        If the task is not complete and then completes successfully, checkers should save the state
        """
        root, child, grandchild = mock_tasks_with_failing_checkers.mock_tasks.values()

        root()
        root.assert_all_tasks_ran()
        root.assert_all_checkers_ran()
        root.assert_all_checkers_saved()
        root.reset_mocks()

        child()
        root.assert_tasks_ran(child=True, grandchild=True)
        root.assert_checkers_ran(child=True, grandchild=True)
        root.assert_checkers_saved(child=True, grandchild=True)
        root.reset_mocks()

        grandchild()
        root.assert_tasks_ran(grandchild=True)
        root.assert_checkers_ran(grandchild=True)
        root.assert_checkers_saved(grandchild=True)
        root.reset_mocks()

    def test_run_if_dependency_runs(self, mock_environment):
        """
        Task should always run if one of it's dependencies run. The assumption is that if a prior
        step executes, then future ones must be run. All checks still run because they may be
        independent of the dependencies
        """

        # Tests where the lowest dependency always runs.
        root = fake.mock_nested_single_dependency_nodes(
            {"check": [PassingCheck("root")]},
            {"check": [PassingCheck("child")]},
            {"check": [FailingCheck("grandchild")]},
        )

        # nested dependency
        root()
        root.assert_all_tasks_ran()
        root.assert_all_checkers_ran()
        root.assert_all_checkers_saved()
        root.reset_mocks()

        # direct dependency
        root.child()
        root.assert_tasks_ran(child=True, grandchild=True)
        root.assert_checkers_saved(child=True, grandchild=True)
        root.assert_checkers_saved(child=True, grandchild=True)
        root.reset_mocks()

    def test_run_force(self, mock_tasks_with_passing_checkers):
        """
        Test forcing run of task
        - checkers are skipped when forced
        - force doesnt cascade
        - only the task directly called should run
        """
        root, child, grandchild = mock_tasks_with_passing_checkers.mock_tasks.values()

        root(force=True)
        root.assert_checkers_ran(child=True, grandchild=True)
        root.assert_tasks_ran(root=True)
        root.assert_checkers_saved(root=True)
        root.reset_mocks()

        child(force=True)
        root.assert_checkers_ran(grandchild=True)
        root.assert_tasks_ran(child=True)
        root.assert_checkers_saved(child=True)
        root.reset_mocks()

        grandchild(force=True)
        root.assert_no_checkers_ran()
        root.assert_tasks_ran(grandchild=True)
        root.assert_checkers_saved(grandchild=True)
        root.reset_mocks()

    def test_run_force_all(self, mock_tasks_with_passing_checkers):
        """
        Test forcing run of entire dependency tree
        - Checkers should be skipped since they are forced.
        - all checkers should save.
        - all tasks should run.
        """
        root, child, grandchild = mock_tasks_with_passing_checkers.mock_tasks.values()

        root(force_all=True)
        root.assert_all_tasks_ran()
        root.assert_no_checkers_ran()
        root.assert_all_checkers_saved()
        root.reset_mocks()

        child(force_all=True)
        root.assert_no_checkers_ran()
        root.assert_checkers_saved(child=True, grandchild=True)
        root.assert_tasks_ran(child=True, grandchild=True)
        root.reset_mocks()

        grandchild(force_all=True)
        root.assert_tasks_ran(grandchild=True)
        root.assert_no_checkers_ran()
        root.assert_checkers_saved(grandchild=True)
        root.reset_mocks()

    def test_execute_failure(self, mock_tasks_that_fail):
        """
        If a task fails the execution chain should stop.
        :return:
        """
        root, child, grandchild = mock_tasks_that_fail.mock_tasks.values()

        with pytest.raises(ExecuteFailed):
            grandchild()

        root.mock.assert_not_called()
        child.mock.assert_not_called()

    def test_task_superseding_explicit_virtual_target(self, mock_environment):
        """
        If a VirtualTask may be explicitly or implicitly defined. The latter happens when a task
        has a parent that is not registered yet. In both cases if a Task with the same name is
        loaded, it will supersede the task. The Task will take the place of the VirtualTask and
        it will assume the VirtualTask's dependencies
        """

        class MockVirtualTarget(VirtualTarget):
            name = "mock_virtual_target"

        MockVirtualTarget()

        mock_task = fake.mock_task(name="mock_virtual_target")

        # the explicit virtual task should now be registered under the key
        runner = TASKS["mock_virtual_target"]
        assert runner == mock_task.__task__

        # running the task should call the mock_task, since it should now be a dependency
        runner()
        mock_task.mock.assert_called_with()

    def test_virtual_task_superseding_implicit_virtual_target(self, mock_environment):
        """
        If a VirtualTask may be explicitly or implicitly defined. The latter happens when a task
        has a parent that is not registered yet. In both cases if a Task with the same name is
        loaded, it will supersede the task. The Task will take the place of the VirtualTask and
        it will assume the VirtualTask's dependencies

        The same hold for a VirtualTask that may replace an implicit virtual task
        """
        mock_task = fake.mock_task(parent="mock_virtual_target")

        class MockVirtualTarget(VirtualTarget):
            name = "mock_virtual_target"

        MockVirtualTarget()

        # the explicit virtual task should now be registered under the key
        runner = TASKS["mock_virtual_target"]
        assert runner == MockVirtualTarget.__task__

        # running the task should call the mock_task, since it should now be a dependency
        runner()
        mock_task.mock.assert_called_with()

    def test_task_superseding_implicit_virtual_target(self, mock_environment):
        """
        If a VirtualTask may be explicitly or implicitly defined. The latter happens when a task
        has a parent that is not registered yet. In both cases if a Task with the same name is
        loaded, it will supersede the task. The Task will take the place of the VirtualTask and
        it will assume the VirtualTask's dependencies
        """
        fake.mock_task(parent="mock_virtual_target")
        mock_task = fake.mock_task(name="mock_virtual_target")

        # the explicit virtual task should now be registered under the key
        runner = TASKS["mock_virtual_target"]
        assert runner == mock_task.__task__

        # running the task should call the mock_task, since it should now be a dependency
        runner()
        mock_task.mock.assert_called_with()

    def test_virtual_target_with_dependencies(self, mock_task):
        """Test running a virtual target that has dependencies"""

        class MockVirtualTarget(VirtualTarget):
            name = "mock_virtual_target"
            depends = ["mock_task"]

        task = MockVirtualTarget()
        task()

        mock_task.mock.assert_called_with()

    def test_explicit_virtual_target(self, mock_environment):
        """"""

        class MockVirtualTarget(VirtualTarget):
            name = "mock_virtual_target"

        task = MockVirtualTarget()

        # run virtual, it shouldn't do anything.
        task()

    def test_implicit_virtual_target(self, mock_environment):
        """
        If a task defines a parent that does not exist, a VirtualTarget will automatically be
        created. This VirtualTarget may be run as if it were explicitly defined.
        """
        task = fake.mock_task(parent="implicit_virtual_task")

        assert "implicit_virtual_task" in TASKS
        assert type(TASKS["implicit_virtual_task"]) == TaskRunner
        virtual_task_runner = TASKS["implicit_virtual_task"]

        # calling the virtual target should call the mock task since it's a dependency
        virtual_task_runner()
        task.mock.assert_called_with()

    def test_check_setup(self):
        """
        Task.check may by undefined, None, a checker, or a list:
        - if undefined it will be converted to None
        - if a non-list it will be converted to a list
        """
        mock_checker = mock.MagicMock()

        task = fake.mock_task(check=None)
        assert task.__task__.checkers is None

        task = fake.mock_task(check=mock_checker)
        assert task.__task__.checkers == [mock_checker]

        task = fake.mock_task(check=[mock_checker])
        assert task.__task__.checkers == [mock_checker]

    def test_str_representations(self, mock_task, snapshot):
        """
        Sanity test of __str__, __unicode__, __repr__
        """
        runner = mock_task.__task__
        runner.__str__()
        runner.__unicode__()
        runner.__repr__()


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


@pytest.mark.usefixtures("mock_environment")
class TestTaskHelp:
    def test_render_help(self, snapshot):
        class MockTask(Task):
            """This is a mock test"""

            name = "mock_test"
            config = ["{IXIAN}", "{PROJECT_NAME}"]

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
            config = ["{IXIAN}", "{PROJECT_NAME}"]

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

    def test_render_status_passing_checks(self, snapshot, mock_tasks_with_passing_checkers):
        # mock checkers for the tree and test when tree is passing
        self.assert_render_status(snapshot, mock_tasks_with_passing_checkers.__task__)
