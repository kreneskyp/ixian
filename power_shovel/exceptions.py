class AlreadyComplete(Exception):
    """
    Exception thrown when a Task executes but it's checks indicate complete.
    """


class ExecuteFailed(Exception):
    """
    Exception thrown by tasks when execute fails.
    """


class MockExit(BaseException):
    """Thrown by mock_exit to simulate exiting the process"""

    def __init__(self, code):
        self.code = code
