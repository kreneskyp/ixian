import functools

import shovel
shovel_task = shovel.task


TASKS = {}


def decorate_task(func, parent=None, depends=None, check=None, clean=None):
    """Decorate a function turning it into a power_shovel task.

    `depends` may be a single function or a list of tasks. Dependencies are run
    before the task unless their `check` function indicates they are complete.

    `parent` specifies a parent task to add this task to. The task will be
    registered as a dependency so it will run when the parent is called. If no
    task exists with this name, a VirtualTask will be created as a placeholder.
    This allows modules to contribute to common tasks like cleanup.

    `clean` specifies the function to call when the task is run with --clean or
    --clean-all. If no function is specified then nothing will happen.

    `check` may be a single Checker or a list of Checkers. Checkers verify that
    a task is complete. This allows tasks execution to be skipped when not
    needed. Checks may be ignored by using --force or --clean.

    Checks cascade. If a dependency fails it's check then both the dependency
    and parent task will run. Dependency checks may be bypassed with
    --force-all or --clean-all

    :param func: function to decorate
    :param parent: a virtual target to add the function to.
    :param depends: list of tasks that must run before this task.
    :param check: list of Checkers that indicate the task is already complete.
    :param clean: Cleanup function to run if task is run with --clean
    :return: decorated task.
    """

    power_shovel_task = Task(
        func=func,
        depends=depends,
        check=check,
        clean=clean,
        parent=parent)

    # Register with shovel. Shovel expects a function so create another wrapper
    # function around the power_shovel_task.
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return power_shovel_task(*args, **kwargs)
    shovel_task(wrapper)

    # return the Task object so the module receives the task.
    return power_shovel_task


def task(func=None, **kwargs):
    if func is None:
        def decorator(func):
            return decorate_task(func, **kwargs)
        return decorator
    else:
        return decorate_task(func)


class AlreadyComplete(Exception):
    """
    Exception thrown when a Task executes but it's checks indicate complete.
    """

class Task(object):
    """
    A task is a wrapper around functions that adds in various functionality
    such as dependencies and check functions.
    """

    def __init__(self,
        func=None,
        depends=None,
        check=None,
        clean=None,
        parent=None,
        auto_help=True
    ):
        self.func = func
        self.auto_help = auto_help
        self.depends = depends or []
        if check:
            if isinstance(check, (list, tuple)):
                self.checkers = check
            else:
                self.checkers = [check]
        else:
            self.checkers = None
        self.clean = clean

        # add task to task-group if a group is specified
        if parent:
            self.add_to_parent(parent)

        # Add task to global registry. Inherit virtual targets if they exist.
        name = func.__name__
        if name in TASKS:
            task_instance = TASKS[name]
            if isinstance(task_instance, VirtualTarget):
                self.add_dependency(*task_instance.depends)
            else:
                # warning
                print('Duplicate task definition: {}'.format(name))
        else:
            task_instance = self
        TASKS[name] = task_instance

    def __str__(self):
        return '<{}@{} func={}>'.format(
            type(self).__name__, id(self), self.func.__name__)

    def __unicode__(self):
        return '<{}@{} func={}>'.format(
            type(self).__name__, id(self), self.func.__name__)

    def __repr__(self):
        return '<{}@{} func={}>'.format(
            type(self).__name__, id(self), self.func.__name__)

    def add_to_parent(self, name):
        """Add a task to as a dependency of a another task.

        This is a grouping method that allows modules to inject
        dependencies into common targets.

        If the target task is not defined a no-op task will be created to wrap
        the added tasks.

        :param name: name of parent task to add task to
        :return: parent task
        """
        try:
            parent = TASKS[name]
        except KeyError:
            parent = VirtualTarget()
            TASKS[name] = parent
        parent.add_dependency(self)
        return parent

    def __call__(self, *args, **kwargs):
        try:
            self.execute(args, **kwargs)
        except AlreadyComplete:
            logger.info(
                'Already complete. Override with --force or --force-all')
            print('Already complete. Override with --force or --force-all')

    def execute(self, args, **kwargs):
        if '--help' in args or '-h' in args and self.auto_help:
            return self.render_help()
        if '--show' in args or '-h' in args:
            return self.render_show()

        clean = kwargs.get('clean', False)
        clean_all = kwargs.pop('clean-all', False)
        force = kwargs.pop('force', False)
        force_all = kwargs.pop('force-all', False)

        if clean:
            force = True
        if clean_all:
            clean = True
            force_all = True
        if force_all:
            force = True

        if self.clean and clean:
            self.clean()

        # execute dependencies. Ignore completed.
        dependency_kwargs = {
            'clean-all': clean_all,
            'force-all': force_all
        }
        depends_complete = True
        for dependency in self.depends:
            try:
                dependency.execute(**dependency_kwargs)
                depends_complete = False
            except AlreadyComplete:
                pass

        # Execute function if there is one. Targets may not have a function.
        if self.func:
            passes, checkers = self.check(force)
            if depends_complete and passes:
                raise AlreadyComplete()

            else:
                return_value = self.func(*args)
                # save checker only after function has completed successfully
                if checkers:
                    for checker in checkers:
                        checker.save()
                return return_value

    def check(self, force=False):
        checkers = None
        passes = False
        if self.checkers:
            if force:
                passes = False
            elif self.checkers:
                checkers = [checker.clone() for checker in self.checkers]
                checks = [checker.check() for checker in checkers]
                passes = all(checks)
        return passes, checkers

    def add_dependency(self, *tasks):
        self.depends.extend(tasks)

    def render_help(self):
        """render the "help" command

        Displays the builtin python help.
        """
        help(self.func)

    def render_show(self):
        """render the "show" command.

        Display the dependency tree for the command.
        """
        OK_GREEN = '\033[92m'
        ENDC = '\033[0m'

        def render_task(task, indent=0):
            if indent > 4:
                return

            passes, _ = task.check()
            rendered_check = OK_GREEN + 'x' + ENDC if passes else ' '
            if indent:
                spacer = ''.join([' ' for _ in range(indent * 2)])
            else:
                spacer = ''

            print('{spacer}[{check}] {name}'.format(
                check=rendered_check,
                name=task.func.__name__,
                spacer=spacer
            ))
            for dependency in task.depends:
                render_task(dependency, indent=indent+1)

        render_task(self)

    def tree_status(self):
        """Return a tree structure of dependencies and check status"""
        dependencies = [dependency.tree_status()
                        for dependency in self.depends]
        return {
            'check': self.check(),
            'name': self.__name__,
            'dependencies': dependencies
        }


class VirtualTarget(Task):
    """
    A virtual target is a placeholder task that is used for targets that
    don't have a real task registered.
    """
    pass
