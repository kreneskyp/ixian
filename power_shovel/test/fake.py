import uuid
from unittest import mock

from power_shovel import Task


def create_task_class(name=None, parent=None, depends=None):
    """Create a task that runs a unittest.Mock"""

    class MockTaskBase:
        mock = mock.Mock()

        def execute(self, *args, **kwargs):
            self.mock(*args, **kwargs)

    MockTask = type(
        name,
        (MockTaskBase, Task),
        {
            "name": name or str(uuid.uuid4()),
            "parent": parent,
            "depends": depends,
            "category": "testing",
        },
    )

    return MockTask()


def mock_nested_single_dependency_nodes():
    """
    Task tree with structure:
        - root
          - child
            - grandchild
    """
    root = create_task_class(name="root")
    root.child = create_task_class(name="child", parent="root")
    root.grandchild = create_task_class(name="grandchild", parent="child")
    root.mock_tests = [
        root,
        root.child,
        root.grandchild,
    ]
    return root


def mock_single_dependency_node_at_end_of_branch_1():
    """
    Task tree with structure:
        - root
          - child_A
          - child_B
              - grandchild_B1
    """
    root = create_task_class(name="root")
    root.child_A = create_task_class(name="child_A", parent="root")
    root.child_B = create_task_class(name="child_B", parent="root")
    root.grandchild_B1 = create_task_class(name="grandchild_B1", parent="child_B")
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
    root = create_task_class(name="root")
    root.child_A = create_task_class(name="child_A", parent="root")
    root.child_B = create_task_class(name="child_B", parent="root")
    root.grandchild_A1 = create_task_class(name="grandchild_A1", parent="child_A")
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
    root = create_task_class(name="root")
    root.child_A = create_task_class(name="child_A", parent="root")
    root.grandchild_A1 = create_task_class(name="grandchild_A1", parent="child_A")
    root.grandchild_A2 = create_task_class(name="grandchild_A2", parent="child_A")
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
    root = create_task_class(name="root")
    root.child_A = create_task_class(name="child_A", parent="root")
    root.child_B = create_task_class(name="child_B", parent="root")
    root.grandchild_A1 = create_task_class(name="grandchild_A1", parent="child_A")
    root.grandchild_A2 = create_task_class(name="grandchild_A2", parent="child_A")
    root.grandchild_B1 = create_task_class(name="grandchild_B1", parent="child_B")
    root.grandchild_B2 = create_task_class(name="grandchild_B2", parent="child_B")
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
    root = create_task_class(name="root")
    root.common_setup = create_task_class(name="common_setup", parent="root")
    root.child_A = create_task_class(
        name="child_A", parent="root", depends=["common_setup"]
    )
    root.child_B = create_task_class(
        name="child_B", parent="root", depends=["common_setup"]
    )
    root.grandchild_B1 = create_task_class(
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
