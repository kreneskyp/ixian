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

import uuid
from unittest import mock

from ixian import runner
from ixian.task import Task
from ixian.exceptions import ExecuteFailed
from ixian.tests.mock_checker import PassingCheck, FailingCheck


def build_test_args(**extra):
    """
    Build list of args for a test. `extra` args are combined with `DEFAULT_ARGS`
    :param extra: extra args to add
    :return: list of args to pass to a TaskRunner
    """
    args = runner.DEFAULT_ARGS.copy()
    args["task_args"] = []
    args.update(extra)
    return args


class MockTaskBase:
    def __init__(self):
        self.mock = mock.Mock(f"{self.name}-execute")
        self.mock_tasks = {}

    def execute(self, *args, **kwargs):
        self.mock(*args, **kwargs)

    def reset_mocks(self):
        """
        Reset all mock functions for all mocked tasks:
        - task execute
        - checker check
        - checker save
        """
        for mock_task in self.mock_tasks.values():
            mock_task.mock.reset_mock()
            mock_task.reset_checkers()
            print("clean?", mock_task.__task__.clean, type(mock_task.__task__.clean))
            if isinstance(mock_task.__task__.clean, mock.Mock):
                mock_task.__task__.clean.reset_mock()

    def reset_checkers(self):
        """Reset any mock checkers"""
        for checker in self.__task__.checkers or []:
            if isinstance(checker.check, mock.Mock):
                checker.check.reset_mock()
            if isinstance(checker.save, mock.Mock):
                checker.save.reset_mock()

    def assert_tasks_ran(self, default=False, **expected):
        for key, task in self.mock_tasks.items():
            if expected.get(key, default):
                task.mock.assert_called_once_with()
            else:
                task.mock.assert_not_called()

    def assert_checkers_ran(self, default=False, **expected):
        for key, task in self.mock_tasks.items():
            if expected.get(key, default):
                task.__task__.checkers[0].check.assert_called_once_with()
            else:
                task.__task__.checkers[0].check.assert_not_called()

    def assert_checkers_saved(self, default=False, **expected):
        for key, task in self.mock_tasks.items():
            if expected.get(key, default):
                task.__task__.checkers[0].save.assert_called_once_with()
            else:
                task.__task__.checkers[0].save.assert_not_called()

    def assert_cleaners_ran(self, default=False, **expected):
        for key, task in self.mock_tasks.items():
            if expected.get(key, default):
                task.__task__.clean.assert_called_once_with()
            else:
                task.__task__.clean.assert_not_called()

    def assert_all_tasks_ran(self):
        self.assert_tasks_ran(default=True)

    def assert_all_cleaners_ran(self):
        self.assert_cleaners_ran(default=True)

    def assert_no_calls(self):
        self.assert_tasks_ran(default=False)

    def assert_all_checkers_ran(self):
        self.assert_checkers_ran(default=True)

    def assert_no_checkers_ran(self):
        self.assert_checkers_ran(default=False)

    def assert_all_checkers_saved(self):
        return self.assert_checkers_saved(default=True)

    def assert_no_checkers_saved(self):
        self.assert_checkers_saved(default=False)


def mock_task(
    name: str = "mock_task", parent: str = None, depends: list = None, **kwargs: dict
) -> MockTaskBase:
    """
    Create a mock task. It calls a mock function when executed. It also provides a number of helper
    functions for testing and resetting a hierarchy of mocked tasks

    :param name: name of task
    :param parent: parents of task
    :param depends: depends of task
    :param kwargs: additional kwargs to pass to class, these become class members.
    :return:
    """
    MockTask = type(
        name,
        (MockTaskBase, Task),
        {
            "name": name or str(uuid.uuid4()),
            "parent": parent,
            "depends": depends,
            "category": "testing",
            **kwargs,
        },
    )

    return MockTask()


def mock_nested_single_dependency_nodes(
    root_kwargs=None, child_kwargs=None, grandchild_kwargs=None
):
    """
    Task tree with structure:
        - root
          - child
            - grandchild
    """

    root = mock_task(name="root", **root_kwargs or {})
    root.child = mock_task(name="child", parent="root", **child_kwargs or {})
    root.grandchild = mock_task(name="grandchild", parent="child", **grandchild_kwargs or {})
    root.mock_tasks = {"root": root, "child": root.child, "grandchild": root.grandchild}

    return root


def mock_tasks_with_clean_functions():
    """
    Setup nested single dependency nodes with mock clean functions
    """

    return mock_nested_single_dependency_nodes(
        {"clean": mock.Mock(name="root-clean")},
        {"clean": mock.Mock(name="child-clean")},
        {"clean": mock.Mock(name="grandchild-clean")},
    )


def mock_tasks_with_passing_checkers():
    return mock_nested_single_dependency_nodes(
        {"check": [PassingCheck("root")]},
        {"check": [PassingCheck("child")]},
        {"check": [PassingCheck("grandchild")]},
    )


def mock_tasks_with_failing_checkers():
    return mock_nested_single_dependency_nodes(
        {"check": [FailingCheck("root")]},
        {"check": [FailingCheck("child")]},
        {"check": [FailingCheck("grandchild")]},
    )


def mock_failing_tasks():
    """
    Mock tests that always raise ExecuteFailed when executed.
    :return:
    """
    root = mock_nested_single_dependency_nodes()
    root.mock.side_effect = ExecuteFailed
    root.child.mock.side_effect = ExecuteFailed
    root.grandchild.mock.side_effect = ExecuteFailed
    return root


def mock_single_dependency_node_at_end_of_branch_1():
    """
    Task tree with structure:
        - root
          - child_A
          - child_B
              - grandchild_B1
    """
    root = mock_task(name="root")
    root.child_A = mock_task(name="child_A", parent="root")
    root.child_B = mock_task(name="child_B", parent="root")
    root.grandchild_B1 = mock_task(name="grandchild_B1", parent="child_B")
    root.mock_tests = [
        root,
        root.child_A,
        root.child_B,
        root.grandchild_B1,
    ]
    return root


def mock_single_dependency_node_at_end_of_branch_2():
    """
    Task tree with structure:
        - root
          - child_A
            - grandchild_A1
          - child_B
    """
    root = mock_task(name="root")
    root.child_A = mock_task(name="child_A", parent="root")
    root.child_B = mock_task(name="child_B", parent="root")
    root.grandchild_A1 = mock_task(name="grandchild_A1", parent="child_A")
    root.mock_tests = [
        root,
        root.child_A,
        root.child_B,
        root.grandchild_A1,
    ]
    return root


def mock_single_dependency_in_middle_of_branch():
    """
    Task tree with structure:
        - root
          - child_A
            - grandchild_A1
            - grandchild_A2
    """
    root = mock_task(name="root")
    root.child_A = mock_task(name="child_A", parent="root")
    root.grandchild_A1 = mock_task(name="grandchild_A1", parent="child_A")
    root.grandchild_A2 = mock_task(name="grandchild_A2", parent="child_A")
    root.mock_tests = [
        root,
        root.child_A,
        root.grandchild_A1,
        root.grandchild_A2,
    ]
    return root


def mock_nested_multiple_dependency_nodes():
    """
    Task tree with structure:
        - root
          - child_A
            - grandchild_A1
            - grandchild_A2
          - child_B
            - grandchild_B1
            - grandchild_B2
    """
    root = mock_task(name="root")
    root.child_A = mock_task(name="child_A", parent="root")
    root.child_B = mock_task(name="child_B", parent="root")
    root.grandchild_A1 = mock_task(name="grandchild_A1", parent="child_A")
    root.grandchild_A2 = mock_task(name="grandchild_A2", parent="child_A")
    root.grandchild_B1 = mock_task(name="grandchild_B1", parent="child_B")
    root.grandchild_B2 = mock_task(name="grandchild_B2", parent="child_B")
    root.mock_tests = [
        root,
        root.child_A,
        root.child_B,
        root.grandchild_A1,
        root.grandchild_A2,
        root.grandchild_B1,
        root.grandchild_B2,
    ]
    return root


def mock_common_dependency():
    """
    Tasks can share a common dependency. This often happens when there is a common setup task. This
    causes the task to appear multiple places in the tree. The extra tasks are deduped but the
    runner.

    Task tree with structure:
        - root
          - common_setup
          - child_A
            - common_setup
          - child_B
            - common_setup
            - grandchild_B1
                - common_setup
    """
    root = mock_task(name="root")
    root.common_setup = mock_task(name="common_setup", parent="root")
    root.child_A = mock_task(name="child_A", parent="root", depends=["common_setup"])
    root.child_B = mock_task(name="child_B", parent="root", depends=["common_setup"])
    root.grandchild_B1 = mock_task(
        name="grandchild_B1", parent="child_A", depends=["common_setup"]
    )
    root.mock_tests = [
        root,
        root.common_setup,
        root.child_A,
        root.child_B,
        root.grandchild_B1,
    ]
    return root


MOCK_TASKS = {
    "nested_single_dependency_nodes": mock_nested_single_dependency_nodes,
    "single_dependency_node_at_end_of_branch_1": mock_single_dependency_node_at_end_of_branch_1,
    "single_dependency_node_at_end_of_branch_2": mock_single_dependency_node_at_end_of_branch_2,
    "single_dependency_in_middle_of_branch": mock_single_dependency_in_middle_of_branch,
    "nested_multiple_dependency_nodes": mock_nested_multiple_dependency_nodes,
    "common_dependency": mock_common_dependency,
}
