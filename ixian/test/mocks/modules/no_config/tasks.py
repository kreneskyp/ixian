from ixian.task import Task


class TestTask(Task):
    """
    This is just a simple task that is functional but doesnt do anything
    """

    name = "test_task"

    def execute(self):
        pass
