.. Ixian documentation master file, created by
   sphinx-quickstart on Sat May  9 03:30:08 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

##################
Ixian
##################

.. toctree::
   :maxdepth: 2
   :caption: Usage:
   :hidden:

   Running Tasks <runner>
   Writing Tasks <tasks>
   Dependency Checking <check>
   Configuration <config>
   Modules <modules>



Ixian is a modular task tool written in python3. It is intended to be a
replacement for Make, emulating and expanding on some of it's most useful
features.

**************
Installation
**************

.. code-block:: bash

   pip install ixian

**************
Setup
**************

Create an :code:`ixian.py` file in the directory where you intend to call :code:`ix` from. Optionally set
:code:`IXIAN_CONFIG` to tell ixian where to find it.

Within :code:`ixian.py` create an :code:`init` method that loads modules and configures settings.

.. code-block:: python

   from ixian.config import CONFIG
   from ixian.module import load_module


   def init():
       # Load modules which contain tasks
       load_module('ixian.modules.core')

       # Update settings
       CONFIG.PROJECT_NAME = 'testing'

*********************
Create a Task
*********************

Tasks are created by extending the task class.

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

*********************
Run a task
*********************

The task may then be called using the :code:`ix` runner.

.. code-block:: bash

   ix my_task

Args passed to the runner are passed to the task as :code:`args`

.. code-block:: bash

   ix my_task arg1 arg2

*********************
Builtin help
*********************

A list of available commands is available by calling :code:`ix` or :code:`ix --help`.

Access built-in help for any task by calling :code:`ix help my_task`. Builtin help should display how to
use the task, enumerate any relevent environment variables, and display the status of any checks.



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`



