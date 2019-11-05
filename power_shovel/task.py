import io

from power_shovel.config import CONFIG
from power_shovel import logger
from power_shovel.utils.color_codes import BOLD_WHITE, ENDC, GRAY, OK_GREEN

TASKS = {}


def clear_task_registry():
    global TASKS
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

    return TaskRunner(
        func=func,
        category=category,
        check=check,
        clean=clean,
        config=config,
        depends=depends,
        parent=parent,
        short_description=short_description,
    )


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


class TaskRunner(object):
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
        description=None,
    ):
        self.func = func
        self._depends = depends or []
        self.category = category.upper() if category else None
        self.clean = clean
        self.short_description = short_description or ""
        self.config = config

        # determine task name
        if name is not None:
            self.name = name
        elif func is not None:
            self.name = func.__name__
        else:
            raise Exception("Either func or name must be given.")

        # determine description
        if name is not None:
            self.description = description
        elif func is not None and hasattr(func, "__doc__"):
            self.description = func.__doc__
        else:
            self.description = ""

        # Add task to global registry. Merge virtual target's dependencies if
        # they exist.
        if self.name in TASKS:
            task_instance = TASKS[self.name]
            # The task is virtual if there is no func, replace it.
            if task_instance.func is None:
                self.add_dependency(*task_instance._depends)
                task_instance = self
            else:
                logger.warn("Duplicate task definition: {}".format(self.name))
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
        return "<{}@{} func={}>".format(type(self).__name__, id(self), self.name)

    def __unicode__(self):
        return "<{}@{} name={}>".format(type(self).__name__, id(self), self.name)

    def __repr__(self):
        return "<{}@{} name={}>".format(type(self).__name__, id(self), self.name)

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
            # VirtualTarget wasn't defined explicitly, or task hasn't been loaded yet.
            # create a TaskRunner for the target. If an explicit task is loaded after
            # it will replace this and assume the children that were already added.
            parent = TaskRunner(name=name)
            TASKS[name] = parent
        parent.add_dependency(self)
        return parent

    def __call__(self, *args, **kwargs):
        self.execute(args, **kwargs)

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
        clean = kwargs.get("clean", False)
        clean_all = kwargs.pop("clean_all", False)
        force = kwargs.pop("force", False)
        force_all = kwargs.pop("force_all", False)

        if clean:
            force = True
        if clean_all:
            clean = True
            force_all = True
        if force_all:
            force = True

        self.force = True

        args_as_str = CONFIG.format(" ".join([str(arg) for arg in args]))
        logger.debug(
            "[exec] {}({}) force={} clean={}".format(
                self.name, args_as_str, force, clean
            )
        )

        if self.clean and clean:
            logger.debug("Cleaning Task: {}".format(self.clean))
            self.clean()

        # execute dependencies. Ignore completed.
        dependency_kwargs = {"clean_all": clean_all, "force_all": force_all}
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
                logger.debug("[skip] {}, already complete.".format(self.name))
                raise AlreadyComplete()

            else:
                return_value = self.func(*args)
                # save checker only after function has completed successfully
                if checkers:
                    for checker in checkers:
                        checker.save()
                logger.debug("[fini] {}".format(self.name))
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
            dependency if isinstance(dependency, TaskRunner) else TASKS[dependency]
            for dependency in self._depends
        ]

    def render_help(self, buffer):
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

        buffer.write(BOLD_WHITE)
        buffer.write("NAME\n")
        buffer.write(ENDC)
        buffer.write(
            "    {task} -- {short_description}\n".format(
                task=self.name, short_description=self.short_description
            )
        )
        buffer.write(BOLD_WHITE)
        buffer.write("\nDESCRIPTION\n")
        buffer.write(ENDC)
        if self.description:
            buffer.write(CONFIG.format(self.description))

        if self.config:
            buffer.write(BOLD_WHITE)
            buffer.write("\nCONFIGURATION\n")
            buffer.write(ENDC)
            padding = max(len(config) for config in self.config) - 1
            for config in self.config:
                buffer.write(
                    "    - {key}  {value}\n".format(
                        key="{key}:".format(key=config[1:-1]).ljust(padding),
                        value=CONFIG.format(config),
                    )
                )

        buffer.write(BOLD_WHITE)
        buffer.write("\n\nSTATUS\n")
        buffer.write(ENDC)
        self.render_status(buffer)

    def render_status(self, buffer):
        """render task status.

        Display the dependency tree for the task.

        Formatting/Readability optimizations:
         - Tree trimming: Redundant nodes are trimmed from the status tree.
            If A and B both depend on C then C will only be shown once.
        """

        def render_task(node, indent=0):
            # render task status
            if node["name"] is not None:
                passes = node["passes"]
                if passes:
                    icon = OK_GREEN + "✔" + ENDC
                else:
                    icon = GRAY + "○" + ENDC
                if indent:
                    spacer = "  " * indent
                else:
                    spacer = ""

                task_line = f'{spacer}{icon} {node["name"]}\n'
                buffer.write(task_line)
                indent += 1

            for dependency in node["dependencies"]:
                render_task(dependency, indent=indent)

        render_task(self.status(), indent=2)

    def tree(self, dedupe: bool = True, flatten: bool = True) -> dict:
        """
        Return tree of tasks, with this task as the root.

        :param dedupe: remove duplicates from tree
        :param flatten: flatten single item dependcy lists into the parent
        :return:
        """
        tree = self._build_tree(set([]) if dedupe else None)
        if flatten:
            tree = flatten_tree(tree)
        return tree

    def _build_tree(self, seen=None):
        """
        Internal method for recursively building task tree
        :param seen: should be a Set if deduping.
        :return: node in tree
        """
        dependencies = []
        for dependency in self.depends:
            if seen is not None:
                if dependency in seen:
                    continue
                seen.add(dependency)
            dependencies.append(dependency._build_tree(seen))

        return {"name": self.name, "dependencies": dependencies}

    def status(self, dedupe: bool = True, flatten: bool = True) -> dict:
        """
        Return the task tree augmented with status information
        """

        def update(node):
            for dependency in node["dependencies"]:
                update(dependency)

            if node["name"] is not None:
                # Run self.check even if children fail their checks. That way the
                # checkers (and state) are available.
                children_passes = all(
                    (dependency["passes"] for dependency in node["dependencies"])
                )
                runner = TASKS[node["name"]]
                passes, checkers = runner.check()
                node["checkers"] = checkers

                # node fails if any children have failed
                node["passes"] = passes and children_passes

            return node

        return update(self.tree(dedupe, flatten))


def flatten_tree(tree: dict, full: bool = False) -> dict:
    """
    Flatten an execution tree to make it easier to read.

    Task trees are often a single node nested several levels deep. These trees may be collapsed
    into a list. The execution order is the same, but it's easier for a human to read.

    Before:
        - foo
          - bar
            - xoo

    After:
        - xoo
        - bar
        - foo


    Before:
        - foo
          - xar
          - bar
            - xoo

    After:
        - foo
          - xar
          - xoo
          - bar

    :param tree: Tree to flatten
    :param full: Flatten tree into single list
    :return: flattened task list
    """

    def flatten_node(node: dict) -> list:
        """
        Flatten a single node. Always return a list for consistency, even when returning a single
        node.

        :param node:
        :param parent: parent task list to collapse into
        :return: flattened node
        """
        node = node.copy()
        num_dependencies = len(node["dependencies"])
        if num_dependencies == 0:
            # no dependencies: nothing to flatten, return as-is
            return [node]

        elif full or num_dependencies == 1:
            # flatten dependencies: flatten into single list that includes parent & child
            flattened = []
            for dependency in node["dependencies"]:
                flattened_child = flatten_node(dependency)
                flattened.extend(flattened_child)

                # clear dependencies, since they are now siblings
                # this node is added last since it runs after dependencies
                node["dependencies"] = []
                flattened.append(node)

            return flattened

        else:
            # multiple dependencies: do not flatten into parent.
            #
            # Any dependencies that are flattened need to be merged with other dependencies.
            # Dependency nodes should either be a single node, or a list of nodes
            dependencies = []
            for dependency in node["dependencies"]:
                flattened = flatten_node(dependency)
                dependencies.extend(flattened)

            node["dependencies"] = dependencies
            return [node]

    root = flatten_node(tree)
    if len(root) > 1:
        # if root's dependencies were flattened into it, then the returned list will have all of
        # those dependencies. Create a new root node to contain them all. This keeps the structure
        # consistent-ish for downstream consumers. They still have to special case this node, but
        # it should be a little simpler since all nodes are of a similar shape
        return {"name": None, "dependencies": root}
    else:
        # a single node, unpack it and return as root.
        return root[0]


class Task(object):
    """
    Super class for defining power_shovel tasks.

    Task subclasses should define an execute method.
    """

    __task__ = None

    @property
    def __func__(self):
        if not hasattr(self, "execute"):
            raise NotImplementedError("Task classes must implement execute method")

        # wrap execute method to curry `self`
        def execute(*args, **kwargs):
            return self.execute(*args, **kwargs)

        return execute

    def __new__(cls, *args, **kwargs):
        instance = super(Task, cls).__new__(cls, *args, **kwargs)

        if cls.__task__ is None:
            cls.__task__ = TaskRunner(
                func=instance.__func__,
                name=instance.name,
                category=getattr(instance, "category", None),
                depends=getattr(instance, "depends", None),
                check=getattr(instance, "check", None),
                clean=getattr(instance, "clean", None),
                config=getattr(instance, "config", None),
                parent=getattr(instance, "parent", None),
                short_description=getattr(instance, "short_description", None),
                description=cls.__doc__,
            )

        return instance

    def __call__(self, *args, **kwargs):
        type(self).__task__(*args, **kwargs)


class VirtualTarget(Task):
    """
    A virtual target is a placeholder task that is used for targets that
    don't have a concrete task registered. VirtualTargets may be executed the
    same as tasks. When run, they execute dependencies that were registered
    with them.

    VirtualTargets allow the target to be given a description, dependencies,
    and other options. VirtualTargets allow tasks grouping without tight
    coupling to a specific target.

    Tasks and other VirtualTargets register with another VirtualTarget by
    specifying the targets as it's parent.  I.e. `parent='my_target'`.

    If multiple modules implement VirtualTargets with the same name, then they
    will be merged. This allows modules to define the same groupings.

    For example, javascript and python modules might both define a `test`
    target to encapsulate all tests. Build pipeline tools can be built to
    expect the generic `test` target regardless of whether a project use
    python, javascript, or any other combination of languages.

    If a concrete Task with the same name as VirtualTarget is registered, the
    Task will replace the VirtualTarget. Tasks that contribute to the virtual
    target act as dependencies, they'll run before any concrete task.
    """

    @property
    def __func__(self):
        return None
