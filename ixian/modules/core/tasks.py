import io

from ixian.task import Task, VirtualTarget


class Lint(VirtualTarget):
    """Virtual target for linting project."""

    name = "lint"
    category = "testing"
    short_description = "Run all linting tasks."


class Test(VirtualTarget):
    """Virtual target for running all tests."""

    name = "test"
    category = "testing"
    short_description = "Run all testing tasks."


# =============================================================================
#  Teardown
# =============================================================================


class Clean(VirtualTarget):
    """Virtual target for cleaning the project."""

    name = "clean"
    category = "build"
    short_description = "Run all clean tasks."


class Help(Task):
    """
    Ixian internal help. Displays either internal help or a task's help.
    """

    name = "help"
    short_description = "This help message or help <task> for task help"
    contexts = True

    def execute(self, task_name=None):
        from ixian import runner

        if task_name:
            subtask = runner.resolve_task(task_name)
            buffer = io.StringIO()
            subtask.render_help(buffer)
            print(buffer.getvalue())
            buffer.close()
        else:
            parser = runner.get_parser()
            parser.print_help()
        return 0
