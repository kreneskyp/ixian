##################
Ix runner
##################

The Ix runner is installed with the package. It is the entry point to use Ix. To run a task type:

.. code-block:: bash

    ix my_task


*****************************
Arguments and Flags
*****************************


Command line arguments and flags are passed to tasks as args and kwargs to the
task.

An example and the equivilant call in python.

.. code-block:: bash

    ix my_task arg1 arg2 --flag --two=2


.. code-block:: python

    my_task('arg1', 'arg2', flag=True, two=2)


****************
Builtin options
****************

All tasks have a set of built in options.

:code:`--force`
--------------------

Run the task regardless of whether checkers determine the task is complete.

:code:`--force-all`
--------------------

Run the full dependency tree regardless of completion state.

:code:`--clean`
--------------------

Clean up task artifacts before running the task. This implies :code:`--force`

:code:`--clean-all`
--------------------

Clean up all dependencies before running the dependencies. This implies
:code:`--force-all`.


:code:`--show`
--------------------

Display the dependency tree including which tasks pass their checks.


*********************
Builtin help
*********************

A list of available commands is available by calling :code:`ix` or :code:`ix --help`.

Access built-in help for any task by calling :code:`ix help my_task`. Builtin help should display
how to use the task, enumerate any relevent environment variables, and display the status of any
checks.


*****************************
Ixian.py location
*****************************

By default :code:`ix` will look for :code:`ixian.py` in the current working directory. This may be
changed at runtime by setting :code:`IXIAN_CONFIG`.

.. code-block:: bash

    IXIAN_CONFIG=/path/to/a/different/file.py ix my_task

