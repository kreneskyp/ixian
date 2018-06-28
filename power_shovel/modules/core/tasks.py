from power_shovel import task


@task(
    category='testing',
    short_description='Run all linting tasks.'
)
def lint():
    """Virtual target for linting project."""


@task(
    category='testing',
    short_description='Run all testing tasks.'
)
def test():
    """Virtual target for running all tests."""


# =============================================================================
#  Teardown
# =============================================================================

@task(
    category='build',
    short_description='Run all clean tasks.'
)
def clean():
    """Virtual target for cleaning the project."""


@task(
    short_description='This help message or help <task> for task help'
)
def help(task_name=None):
    from power_shovel import runner
    if task_name:
        subtask = runner.resolve_task(task_name)
        subtask.render_help()
    else:
        parser = runner.get_parser()
        parser.print_help()
    return 0
