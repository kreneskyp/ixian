

*****************************
API
*****************************


Tasks
--------------------

Tasks are created by extending the :code:`task` class. Tasks must define a :code:`name` and
:code:`execute` method.

.. code-block:: python

    from ixian.task import Task

    class MyTask(Task):
        """
        The docstring will be used as help text.
        """

        name = 'my_task'
        short_description = 'description will be shown in general help'

        def execute(self, *args, **kwargs)
            print(args, kwargs)


Tasks are configured by setting class properties:

* :code:`name`: name used to reference task
* :code:`description`: short description of task
* :code:`depends`: list of dependencies
* :code:`parents`: list of parent tasks
* :code:`check`: list of checkers that determine if the task is complete
* :code:`clean`: function to run when --clean is specified


Checkers
--------------------

Checkers determine if a task is complete or not. When a checker determines a 
task is complete it will be skipped unless :code:`--force` or :code:`--clean` is set. There
are built-in checkers and support for custom checkers. 


.. code-block:: python

    from ixian import Task
    from ixian.modules.filesystem.file_hash import FileHash


    class MyTask(Task):
        """
        This task will only run if input_file and output_file are modified or removed.
        """
        name = 'my_task'
        check = [
            FileHash('/input_file'),
            FileHash('/output_file')
        ]


See the [Checker documentation](check.md) for more detail.


Dependencies
--------------------

Tasks may specify depend tasks that must run first. The dependency tree is 
examined and executed automatically. If a dependency's checkers indicate the
task must be run then that part of the dependency tree will be re-run.


.. code-block:: python

    class Parent(Task):
        name = 'parent'
        depends = ['child']

        def execute(self, *args, **kwargs):
            print("parent")


    class Child1(Task):
        """
        whenever parent is called, this dependency runs first.
        """
        name = 'child_1'

        def execute(self, *args, **kwargs):
            print('child 1')


Tasks may also define parents in reverse.

.. code-block:: python

    class Child2(Task):
        """
        This task also is a dependency of parent.
        """
        name = 'child_2'
        parent = ['parent']

        def execute(self, *args, **kwargs):
            print('child 2')



The dependency tree for a task may be viewed by the built-in help

.. code-block:: bash

    ix help parent


The status section lists the tree of tasks and their statuses.

.. code-block:: text

    STATUS
    ○ parent
        ○ child_1
        ○ child_2


State
--------------------

Tasks define their state using checkers. State is used to identify the inputs and provide an
identifier for the expected output for the run.

State is accessible to tasks through :code:`CONFIG`.

.. code-block:: python

    class MyConfig(Config):

        @classproperty
        def TASK_HASH:
            """Hash can be used as the identifier for build artifacts."""
            return "{TASKS.MY_TASK.HASH}"

        @classproperty
        def TASK_STATE:
            """State useful for debugging task trees."""
            return "{TASKS.MY_TASK.STATE}"


Task dependencies are automatically added to task state. If a dependency

.. code-block:: python

    > CONFIG.MY_TASK.STATE

    {

    }