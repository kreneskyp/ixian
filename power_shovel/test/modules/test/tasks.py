from power_shovel.task import task


@task()
def foo(args):
    pass


@task()
def error(args):
    raise Exception('Intentional error.')
