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


class ModuleLoadError(Exception):
    """Error thrown when module can't be loaded"""

    pass


class InvalidClassPath(Exception):
    """Error thrown when a class path is not in the valid format"""

    pass
