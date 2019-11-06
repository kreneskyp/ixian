import uuid
from unittest import mock

from power_shovel import Task
from power_shovel.test.mock_checker import PassingCheck


def mock_task(
    name: str = None, parent: str = None, depends: list = None, **kwargs: dict
) -> Task:
    """
    Create a mock task. It calls a mock function when executed. It also provides a number of helper
    functions for testing and resetting a hierarchy of mocked tasks

    :param name: name of task
    :param parent: parents of task
    :param depends: depends of task
    :param kwargs: additional kwargs to pass to class, these become class members.
    :return:
    """

    class MockTaskBase:
        mock = mock.Mock()
        mock_tasks = []

        def execute(self, *args, **kwargs):
            self.mock(*args, **kwargs)

        def reset_task_mocks(self):
            for mock_task in self.mock_tasks:
                mock_task.mock.reset_mock()

        def reset_task_clean_mocks(self):
            for mock_task in self.mock_tasks:
                mock_task.mock_clean.reset_mock()

        def reset_task_checkers_save(self):
            for mock_task in self.mock_tasks:
                mock_task.checkers[0].save.reset_mock()

        def reset_task_checkers_check(self):
            for mock_task in self.mock_tasks:
                mock_task.checkers[0].check.reset_mock()

        def assert_no_calls(self):
            for mock_task in self.mock_tasks:
                mock_task.mock.assert_has_calls([])

        def assert_no_checker_save_calls(self):
            for mock_task in self.mock_tasks:
                mock_task.checkers[0].save.assert_has_calls([])

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
    root.grandchild = mock_task(
        name="grandchild", parent="child", **grandchild_kwargs or {}
    )
    root.mock_tasks = [
        root,
        root.child,
        root.grandchild,
    ]

    return root


def mock_tasks_with_clean_functions():
    """
    Setup nested single dependency nodes with mock clean functions
    """

    return mock_nested_single_dependency_nodes(
        {"mock_clean": mock.Mock()},
        {"mock_clean": mock.Mock()},
        {"mock_clean": mock.Mock()},
    )


def mock_tasks_with_passing_checkers():
    return mock_nested_single_dependency_nodes(
        {"check": [PassingCheck()]},
        {"check": [PassingCheck()]},
        {"check": [PassingCheck()]},
    )


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
