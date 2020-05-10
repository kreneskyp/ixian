# Copyright [2018-2020] Peter Krenesky
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import typing

from ixian.check.checker import hash_object
from ixian.config import CONFIG
from ixian.exceptions import AlreadyComplete
from ixian.utils.color_codes import BOLD_WHITE, ENDC, GRAY, OK_GREEN


logger = logging.getLogger(__name__)
TASKS = {}


class TaskRunner(object):
    """
    A task is a wrapper around functions that adds in various functionality
    such as dependencies and check functions.

    func - function to run
    category - category to add this task to
    check - list of checkers
    clean - clean before building
    config - list of relevant settings to display in task help
    name - name of this task
    short_description - short description for task
    description - long description for task
    parent - parent task (this task will be run first if it is run)
    children - tasks this task depends on (They will be run first)
    """

    checkers = None

    def __init__(
        self,
        task=None,
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
        self.task = task
        self.func = func
        self._depends = depends or []
        self.category = category.upper() if category else None
        self.clean = clean
        self.short_description = short_description or ""
        self.config = config

        # determine task name
        if name is not None:
            self.name = name

        # determine description
        self.description = description

        # Add task to global registry. Merge virtual target's dependencies if they exist.
        if self.name in TASKS:
            task_instance = TASKS[self.name]
            # The task is virtual if there is no func, replace it.
            if task_instance.func is None:
                self.add_dependency(*task_instance._depends)
                task_instance = self
            else:
                logger.warning("Duplicate task definition: {}".format(self.name))
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

    def __str__(self):
        return f"<{type(self).__name__}@{id(self)} func={self.name}>"

    def __unicode__(self):
        return f"<{type(self).__name__}@{id(self)} func={self.name}>"

    def __repr__(self):
        return f"<{type(self).__name__}@{id(self)} func={self.name}>"

    @property
    def in_context(self):
        if not self.task:
            return False

        return self.task.contexts is True or CONFIG.RUN_CONTEXT in self.task.contexts

    def add_to_parent(self, name: str):
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
        return self.execute(args, **kwargs)

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
        clean_root = kwargs.get("clean", False)
        clean_all = kwargs.pop("clean_all", False)
        force_root = kwargs.pop("force", False)
        force_all = kwargs.pop("force_all", False)

        if clean_root:
            force_root = True
        if clean_all:
            clean_root = True
            force_all = True
        if force_all:
            force_root = True

        # save force to task instance so it may be referenced downstream
        # TODO: this should be passing in `force`
        self.force = True

        args_as_str = CONFIG.format(" ".join([str(arg) for arg in args]))
        logger.debug(f"[exec] {self.name}({args_as_str}) force={force_root} clean={clean_root}")

        def execute_node(node, clean, force, args=None):
            runner = TASKS[node["name"]]

            if runner and runner.clean and clean:
                logger.debug(f"Cleaning Task: {runner.clean}")
                runner.clean()

            complete_dependencies = 0
            for dependency in node["dependencies"]:
                try:
                    execute_node(dependency, clean_all, force_all)
                except AlreadyComplete:
                    complete_dependencies += 1
            dependencies_complete = complete_dependencies == len(node["dependencies"])

            # Execute function if there is one. Targets may not have a function. If any dependency
            # was run, then this task must run too.
            if runner and runner.func:
                passes, checkers = runner.check(force)
                if dependencies_complete and passes:
                    logger.debug(f"[skip] {node['name']}, already complete.")
                    raise AlreadyComplete()

                else:
                    # set tasks force attribute so it's setup the same as if it were run directly.
                    runner.task.__task__.force = force
                    return_value = runner.func(*args or [])
                    # save checker only after function has completed successfully. Save should be
                    # called even if force=True
                    if checkers:
                        for checker in checkers:
                            checker.save()
                    logger.debug(f"[fini] {runner.name}")
                    return return_value

        return execute_node(self.tree(flatten=False), clean_root, force_root, args)

    def check(self, force: bool = False) -> (bool, list):
        """Return True if the task is complete based on configured checks.

        If the task does not have a checker this method always returns `False`.

        :param force: override the check and return True if True.
        :return:
        """
        checkers = [checker.clone() for checker in self.checkers] if self.checkers else None
        passes = False
        if self.checkers:
            if force:
                passes = False
            else:
                checks = [checker.check() for checker in checkers]
                passes = all(checks)
        return passes, checkers

    def state(self, shallow: bool = True) -> typing.Optional[dict]:
        """
        Calculates a dict of state generated from the tasks checkers.

        :param shallow: only return hash for dependencies
        :return: dict of state returned from checkers
        """
        if self.checkers is None and self.depends is None:
            return None

        checkers = (
            [checker.clone() for checker in self.checkers if checker.contribute_to_task_state]
            if self.checkers
            else None
        )

        depends = {}
        for dependency in self.depends:
            name = dependency.name
            if shallow:
                depends[name] = dependency.hash()
            else:
                depends[name] = dependency.state()

        return {
            "depends": depends,
            "checks": [
                {
                    "class": f"{type(checker).__module__}.{type(checker).__name__}",
                    "state": checker.state(),
                }
                for checker in checkers
            ],
        }

    def hash(self):
        return hash_object(self.state(shallow=True))

    def add_dependency(self, *tasks):
        self._depends.extend(tasks)

    @property
    def depends(self) -> list:
        return [
            dependency if isinstance(dependency, TaskRunner) else TASKS[CONFIG.format(dependency)]
            for dependency in self._depends
        ]

    def render_help(self, buffer) -> None:
        """render the "help" command

        Renders ixian internal help for the task. This help should explain
        how to use the task via ixian.

        Many tasks are proxies to other tools (e.g. npm, pipenv, etc). This
        help shouldn't try to replace that. Proxy tasks should indicate as such
        and include an example how to reach the tool's built-in help (--help)

        combines:
          - Name of task
          - Docstring as length description
          - task status tree
        """
        from ixian.config import CONFIG

        buffer.write(BOLD_WHITE)
        buffer.write("NAME\n")
        buffer.write(ENDC)
        buffer.write(f"    {self.name} -- {self.short_description}\n")
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

    def render_status(self, buffer) -> None:
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
                indent += 2

            for dependency in node["dependencies"]:
                render_task(dependency, indent=indent)

        render_task(self.status(), indent=0)

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
    Super class for defining ixian tasks.

    Task subclasses should define an execute method.
    """

    __task__ = None
    contexts = ["cli"]

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

        # TODO: fix needed, for broken tests this causes
        # if instance.name not in TASKS:
        if cls.__task__ is None not in TASKS:
            cls.__task__ = TaskRunner(
                task=instance,
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
        else:
            # In practice task classes should never need to be instantiated more than once.
            # Unloading tasks isn't supported at this time, but tests may do that. When that
            # happens subsequent tests may see this fail. This msg helps show that happened.
            # hopefully this is fixed in a better way when task loading/tree is refactored.
            logger.warning(f"Task {instance.name} instantiated but an instance already exists")

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
