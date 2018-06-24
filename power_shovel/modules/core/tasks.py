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
