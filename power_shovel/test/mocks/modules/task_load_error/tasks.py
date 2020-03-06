from power_shovel.task import Task


class TestTask(Task):
    """
    This task always raises an exception when it's initialized
    """

    name = "test_task"

    def __init__(self):
        raise Exception("Intentional Exception")

    def execute(self):
        pass
