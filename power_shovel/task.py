import functools
import logging

import io

import shovel
from power_shovel import logger
from power_shovel.utils.color_codes import BOLD_WHITE, ENDC

shovel_task = shovel.task

TASKS = {}


def decorate_task(
    func,
    category=None,
    check=None,
    config=None,
    clean=None,
    depends=None,
    parent=None,
    short_description=None,
):
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
    :param category: category name to add task to. Category is only used for
        group tasks in the help menu.
    :param parent: virtual targets to add the function to (string or list).
    :param depends: list of tasks that must run before this task.
    :param check: list of Checkers that indicate the task is already complete.
    :param clean: Cleanup function to run if task is run with --clean
    :param config: Configuration variables (as strings) used by this task.
    :param short_description: help text shown in main --help screen
    :return: decorated task.
    """

    power_shovel_task = Task(
        func=func,
        category=category,
        check=check,
        clean=clean,
        config=config,
        depends=depends,
        parent=parent,
        short_description=short_description,
    )

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

    def __init__(
        self,
        func=None,
        category=None,
        check=None,
        clean=None,
        config=None,
        depends=None,
        name=None,
        parent=None,
        short_description=None,
    ):
        self.func = func
        self._depends = depends or []
        self.category = category.upper() if category else None
        self.clean = clean
        self.short_description = short_description or ''
        self.config = config

        # determine task name
        if func is not None:
            self.name = func.__name__
        elif name is not None:
            self.name = name
        else:
            raise Exception('Either func or name must be given.')

        # Add task to global registry. Merge virtual target's dependencies if
        # they exist.
        if self.name in TASKS:
            task_instance = TASKS[self.name]
            if isinstance(task_instance, VirtualTarget):
                self.add_dependency(*task_instance._depends)
                task_instance = self
            else:
                logger.warn('Duplicate task definition: {}'.format(self.name))
        else:
            task_instance = self
        TASKS[self.name] = task_instance

        # add task to VirtualTargets if a parent is specified
        if parent:
            for parent in parent if isinstance(parent, list) else [parent]:
                self.add_to_parent(parent)

        # Setup checkers, clean method
        if check:
            if isinstance(check, (list, tuple)):
                self.checkers = check
            else:
                self.checkers = [check]
        else:
            self.checkers = None

    def __str__(self):
        return '<{}@{} func={}>'.format(
            type(self).__name__, id(self), self.name)

    def __unicode__(self):
        return '<{}@{} name={}>'.format(
            type(self).__name__, id(self), self.name)

    def __repr__(self):
        return '<{}@{} name={}>'.format(
            type(self).__name__, id(self), self.name)

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
            parent = VirtualTarget(name=name)
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
        """Execute this task.

        Executes this task including any dependencies that fail their checks.
        If a dependency fails it's check then this task will execute even if
        it's own checks pass.

        Tasks and dependencies may be forced by passing `force=True` or
        `force-all=True` as kwargs.

        Tasks and dependency clean methods may be run by passing `clean=True`
        or `clean-all=False` as kwargs. Clean implies `force=True`.

        :param args: args to pass through to the task
        :param kwargs: options for task execution
        :return: return value from task function
        """
        clean = kwargs.get('clean', False)
        clean_all = kwargs.pop('clean_all', False)
        force = kwargs.pop('force', False)
        force_all = kwargs.pop('force_all', False)

        if clean:
            force = True
        if clean_all:
            clean = True
            force_all = True
        if force_all:
            force = True

        logger.debug('Executing [{}] force={} clean={}'.format(
            self.name, force, clean
        ))

        if self.clean and clean:
            logger.debug('Cleaning Task: {}'.format(
                self.clean
            ))
            self.clean()

        # execute dependencies. Ignore completed.
        dependency_kwargs = {
            'clean_all': clean_all,
            'force_all': force_all
        }
        depends_complete = True
        for dependency in self.depends:
            try:
                dependency.execute([], **dependency_kwargs)
                depends_complete = False
            except AlreadyComplete:
                pass

        # Execute function if there is one. Targets may not have a function.
        if self.func:
            passes, checkers = self.check(force)
            if depends_complete and passes:
                logger.debug('Skipping [{}], already complete.'.format(
                    self.name))
                raise AlreadyComplete()

            else:
                return_value = self.func(*args)
                # save checker only after function has completed successfully
                if checkers:
                    for checker in checkers:
                        checker.save()
                return return_value

    def check(self, force=False):
        """Return True if the task is complete based on configured checks.

        If the task does not have a checker this method always returns `False`.

        :param force: override the check and return True if True.
        :return:
        """
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
        self._depends.extend(tasks)

    @property
    def depends(self):
        return [
            dependency if isinstance(dependency, Task) else TASKS[dependency]
            for dependency in self._depends
        ]

    def render_help(self):
        """render the "help" command

        Renders shovel internal help for the task. This help should explain
        how to use the task via shovel.

        Many tasks are proxies to other tools (e.g. npm, pipenv, etc). This
        help shouldn't try to replace that. Proxy tasks should indicate as such
        and include an example how to reach the tool's built-in help (--help)

        combines:
          - Name of task
          - Docstring as length description
          - task status tree
        """
        from power_shovel.config import CONFIG
        buffer = io.StringIO()
        buffer.write(BOLD_WHITE)
        buffer.write('NAME\n')
        buffer.write(ENDC)
        buffer.write('    {task} -- {short_description}\n'.format(
            task=self.name,
            short_description=self.short_description
        ))
        buffer.write(BOLD_WHITE)
        buffer.write('\nDESCRIPTION\n')
        buffer.write(ENDC)
        buffer.write(CONFIG.format(self.func.__doc__))

        if self.config:
            buffer.write(BOLD_WHITE)
            buffer.write('\nCONFIGURATION\n')
            buffer.write(ENDC)
            padding = max(len(config) for config in self.config) - 1
            for config in self.config:
                buffer.write('    - {key}  {value}\n'.format(
                    key='{key}:'.format(key=config[1:-1]).ljust(padding),
                    value=CONFIG.format(config)
                ))

        buffer.write(BOLD_WHITE)
        buffer.write('\n\nSTATUS\n')
        buffer.write(ENDC)
        self.render_status(buffer)
        print(buffer.getvalue())
        buffer.close()

    def render_status(self, buffer):
        """render task status.

        Display the dependency tree for the task.

        Formatting/Readability optimizations:
         - Tree trimming: Redundant nodes are trimmed from the status tree.
            If A and B both depend on C then C will only be shown once.
        """
        OK_GREEN = '\033[92m'
        ENDC = '\033[0m'

        seen = set()

        def render_task(node, indent=0):
            seen.add(node['name'])
            passes = node['passes']
            rendered_check = OK_GREEN + 'x' + ENDC if passes else ' '
            if indent:
                spacer = ''.join([' ' for _ in range(indent * 2)])
            else:
                spacer = ''

            # render task status
            task_line = (
                '{spacer}[{check}] {name}\n'.format(
                    check=rendered_check,
                    name=node['name'],
                    spacer=spacer
                )
            )

            # render dependencies into list. Only increase indent for
            # multi-node-wide dependency chains. Single-node-wide chains are
            # collapsed into the parent.
            dependency_lines = []
            single_dep = len(node['dependencies']) == 1
            next_indent = indent if single_dep else indent + 1
            for dependency in node['dependencies']:
                if dependency['name'] not in seen:
                    dependency_lines.extend(
                        render_task(
                          dependency, indent=next_indent
                        )
                    )

            # Add task and dependency lines. Reverse order for single-node
            # dependency chains. Dependencies run before the parent so when
            # rendered at the same indent they dependencies come first.
            lines = []
            if single_dep:
                lines.extend(reversed(dependency_lines))
                lines.append(task_line)
            else:
                lines.append(task_line)
                lines.extend(dependency_lines)
            return lines

        # Lines are sorted/indented as needed, render to buffer.
        lines = render_task(self.tree_status(), indent=2)
        for line in lines:
            buffer.write(line)

    def tree_status(self):
        """Return a tree structure of dependencies and check status"""
        dependencies = [dependency.tree_status()
                        for dependency in self.depends]

        passes, checkers = self.check()
        return {
            'passes': passes and all((d['passes'] for d in dependencies)),
            'checkers': checkers,
            'name': self.name,
            'dependencies': dependencies
        }


class VirtualTarget(Task):
    """
    A virtual target is a placeholder task that is used for targets that
    don't have a real task registered.
    """
    pass
