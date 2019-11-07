class AlreadyComplete(Exception):
    """
    Exception thrown when a Task executes but it's checks indicate complete.
    """


class ExecuteFailed(Exception):
    """
    Exception thrown by tasks when execute fails.
    """
