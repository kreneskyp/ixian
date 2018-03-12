from unittest import TestCase
from unittest import mock

from power_shovel import task
from power_shovel.test.test_checker import PassingCheck


def create_task(**task_kwargs):
    """Create a task that runs a unittest.Mock"""
    task_mock = mock.Mock()

    @task(**task_kwargs)
    def mocked_task(*args, **kwargs):
        task_mock(*args, **kwargs)

    mocked_task.mock = task_mock
    return mocked_task


def create_dependent_tasks(child_kwargs=None, parent_kwargs=None):
    """Create a task with a dependent task"""
    child = create_task(**(child_kwargs or {}))
    parent = create_task(depends=[child], **(parent_kwargs or {}))
    return parent, child


def create_nested_dependency(
        child_kwargs=None,
        parent_kwargs=None,
        grandparent_kwargs=None):
    """Create two levels of dependencies"""
    parent, child = create_dependent_tasks(child_kwargs, parent_kwargs)
    grandparent = create_task(depends=[parent], **(grandparent_kwargs or {}))
    return grandparent, parent, child


CALL = mock.call()
DEPENDENT_CALL = mock.call(**{'clean-all': False, 'force-all': False})


class TaskTestCases(TestCase):

    def setup_tasks(
            self,
            child_kwargs=None,
            parent_kwargs=None,
            grandparent_kwargs=None):
        """setup tasks"""
        self.grandparent, self.parent, self.child = create_nested_dependency(
            child_kwargs, parent_kwargs, grandparent_kwargs)
        return self.grandparent, self.parent, self.child

    def reset_task_mocks(self):
        self.grandparent.mock.reset_mock()
        self.parent.mock.reset_mock()
        self.child.mock.reset_mock()

    def assert_no_calls(self):
        self.grandparent.mock.assert_has_calls([])
        self.parent.mock.assert_has_calls([])
        self.child.mock.assert_has_calls([])

    def test_task(self):
        """Test running a single task"""
        mocked_task = create_task()
        mocked_task(1, 2, three=3)
        call = mock.call(1, 2, three=3)
        mocked_task.mock.assert_has_calls([call])

    def test_dependency(self):
        """Test running dependant tasks"""
        self.setup_tasks()

        self.grandparent()
        self.grandparent.mock.assert_has_calls([CALL])
        self.parent.mock.assert_has_calls([CALL])
        self.child.mock.assert_has_calls([CALL])
        self.reset_task_mocks()

        self.parent()
        self.grandparent.mock.assert_has_calls([])
        self.parent.mock.assert_has_calls([CALL])
        self.child.mock.assert_has_calls([CALL])
        self.reset_task_mocks()

        self.child()
        self.grandparent.mock.assert_has_calls([])
        self.parent.mock.assert_has_calls([])
        self.child.mock.assert_has_calls([CALL])

    def setup_tasks_with_clean_tasks(self):
        """Create task tree with clean tasks attached"""
        grandparent_clean = mock.Mock()
        parent_clean = mock.Mock()
        child_clean = mock.Mock()
        grandparent, parent, child = self.setup_tasks(
            {'clean': child_clean},
            {'clean': parent_clean},
            {'clean': grandparent_clean})
        grandparent.mock_clean = grandparent_clean
        parent.mock_clean = parent_clean
        child.mock_clean = child_clean
        return grandparent, parent, child

    def reset_task_clean_mocks(self):
        self.grandparent.mock_clean.reset_mock()
        self.parent.mock_clean.reset_mock()
        self.child.mock_clean.reset_mock()

    def test_clean(self):
        """Test forcing clean of task"""
        grandparent, parent, child = self.setup_tasks_with_clean_tasks()

        grandparent(clean=True)
        grandparent.mock_clean.assert_has_calls([CALL])
        parent.mock_clean.assert_has_calls([])
        child.mock_clean.assert_has_calls([])
        self.grandparent.mock.assert_has_calls([CALL])
        self.parent.mock.assert_has_calls([])
        self.child.mock.assert_has_calls([])
        self.reset_task_mocks()
        self.reset_task_clean_mocks()

        parent(clean=True)
        grandparent.mock_clean.assert_has_calls([])
        parent.mock_clean.assert_has_calls([CALL])
        child.mock_clean.assert_has_calls([])
        self.grandparent.mock.assert_has_calls([])
        self.parent.mock.assert_has_calls([CALL])
        self.child.mock.assert_has_calls([])
        self.reset_task_mocks()
        self.reset_task_clean_mocks()

        child(clean=True)
        grandparent.mock_clean.assert_has_calls([])
        parent.mock_clean.assert_has_calls([])
        child.mock_clean.assert_has_calls([CALL])
        self.grandparent.mock.assert_has_calls([])
        self.parent.mock.assert_has_calls([])
        self.child.mock.assert_has_calls([CALL])

    def test_clean_all(self):
        """Test forcing clean of entire dependency tree before run"""
        grandparent, parent, child = self.setup_tasks_with_clean_tasks()

        grandparent(**{'clean-all': True})
        grandparent.mock_clean.assert_has_calls([CALL])
        parent.mock_clean.assert_has_calls([CALL])
        child.mock_clean.assert_has_calls([CALL])
        self.grandparent.mock.assert_has_calls([CALL])
        self.parent.mock.assert_has_calls([CALL])
        self.child.mock.assert_has_calls([CALL])
        self.reset_task_mocks()
        self.reset_task_clean_mocks()

        parent(**{'clean-all': True})
        grandparent.mock_clean.assert_has_calls([])
        parent.mock_clean.assert_has_calls([CALL])
        child.mock_clean.assert_has_calls([CALL])
        self.grandparent.mock.assert_has_calls([])
        self.parent.mock.assert_has_calls([CALL])
        self.child.mock.assert_has_calls([CALL])
        self.reset_task_mocks()
        self.reset_task_clean_mocks()

        child(**{'clean-all': True})
        grandparent.mock_clean.assert_has_calls([])
        parent.mock_clean.assert_has_calls([])
        child.mock_clean.assert_has_calls([CALL])
        self.grandparent.mock.assert_has_calls([])
        self.parent.mock.assert_has_calls([])
        self.child.mock.assert_has_calls([CALL])

    def setup_tasks_with_passing_checkers(self):
        """Create task tree with clean tasks attached"""
        grandparent, parent, child = self.setup_tasks(
            {'check': [PassingCheck()]},
            {'check': [PassingCheck()]},
            {'check': [PassingCheck()]})
        return grandparent, parent, child

    def assert_no_checker_save_calls(self):
        self.grandparent.checkers[0].save.assert_has_calls([])
        self.parent.checkers[0].save.assert_has_calls([])
        self.child.checkers[0].save.assert_has_calls([])

    def reset_task_checkers_save(self):
        self.grandparent.checkers[0].save.reset_mock()
        self.parent.checkers[0].save.reset_mock()
        self.child.checkers[0].save.reset_mock()

    def reset_task_checkers_check(self):
        self.grandparent.checkers[0].check.reset_mock()
        self.parent.checkers[0].check.reset_mock()
        self.child.checkers[0].check.reset_mock()

    def test_checker(self):
        """Test calling checkers"""
        self.setup_tasks_with_passing_checkers()
        grandparent_checker = self.grandparent.checkers[0]
        parent_checker = self.parent.checkers[0]
        child_checker = self.child.checkers[0]

        self.grandparent()
        grandparent_checker.check.assert_has_calls([])
        parent_checker.check.assert_has_calls([])
        child_checker.check.assert_has_calls([])
        self.assert_no_calls()
        self.assert_no_checker_save_calls()
        self.reset_task_checkers_check()

        self.parent()
        grandparent_checker.check.assert_has_calls([])
        parent_checker.check.assert_has_calls([])
        child_checker.check.assert_has_calls([])
        self.assert_no_calls()
        self.assert_no_checker_save_calls()
        self.reset_task_checkers_check()

        self.child()
        grandparent_checker.check.assert_has_calls([])
        parent_checker.check.assert_has_calls([])
        child_checker.check.assert_has_calls([])
        self.assert_no_calls()
        self.assert_no_checker_save_calls()
        self.reset_task_checkers_check()

    def test_force(self):
        """Test forcing run of task"""
        self.setup_tasks_with_passing_checkers()
        grandparent_checker = self.grandparent.checkers[0]
        parent_checker = self.parent.checkers[0]
        child_checker = self.child.checkers[0]

        self.grandparent(force=True)
        grandparent_checker.check.assert_has_calls([])
        parent_checker.check.assert_has_calls([])
        child_checker.check.assert_has_calls([])
        self.grandparent.mock.assert_has_calls([CALL])
        self.parent.mock.assert_has_calls([])
        self.child.mock.assert_has_calls([])
        self.reset_task_checkers_check()

        self.parent(force=True)
        grandparent_checker.check.assert_has_calls([])
        parent_checker.check.assert_has_calls([])
        child_checker.check.assert_has_calls([])
        self.grandparent.mock.assert_has_calls([])
        self.parent.mock.assert_has_calls([CALL])
        self.child.mock.assert_has_calls([])
        self.reset_task_checkers_check()

        self.child(force=True)
        grandparent_checker.check.assert_has_calls([])
        parent_checker.check.assert_has_calls([])
        child_checker.check.assert_has_calls([])
        self.grandparent.mock.assert_has_calls([])
        self.parent.mock.assert_has_calls([])
        self.child.mock.assert_has_calls([CALL])
        self.reset_task_checkers_check()

    def test_force_all(self):
        """Test forcing run of entire dependency tree"""
        self.setup_tasks_with_passing_checkers()
        grandparent_checker = self.grandparent.checkers[0]
        parent_checker = self.parent.checkers[0]
        child_checker = self.child.checkers[0]

        self.grandparent(**{'force-all': True})
        grandparent_checker.check.assert_has_calls([])
        parent_checker.check.assert_has_calls([])
        child_checker.check.assert_has_calls([])
        self.grandparent.mock.assert_has_calls([CALL])
        self.parent.mock.assert_has_calls([CALL])
        self.child.mock.assert_has_calls([CALL])
        self.reset_task_checkers_check()

        self.parent(**{'force-all': True})
        grandparent_checker.check.assert_has_calls([])
        parent_checker.check.assert_has_calls([])
        child_checker.check.assert_has_calls([])
        self.grandparent.mock.assert_has_calls([])
        self.parent.mock.assert_has_calls([CALL])
        self.child.mock.assert_has_calls([CALL])
        self.reset_task_checkers_check()

        self.child(**{'force-all': True})
        grandparent_checker.check.assert_has_calls([])
        parent_checker.check.assert_has_calls([])
        child_checker.check.assert_has_calls([])
        self.grandparent.mock.assert_has_calls([])
        self.parent.mock.assert_has_calls([])
        self.child.mock.assert_has_calls([CALL])
        self.reset_task_checkers_check()

    def test_tree(self):
        """Test generating dependency tree data"""
        raise NotImplementedError
