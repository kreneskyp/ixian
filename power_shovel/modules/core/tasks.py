from power_shovel import task


@task()
def lint():
    """Virtual target for linting project."""


@task()
def test():
    """Virtual target for running all tests."""


# =============================================================================
#  Teardown
# =============================================================================

@task()
def clean():
    """Virtual target for cleaning the project."""



@task()
def teardown():
    """Shutdown running processes"""

