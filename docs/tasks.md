# Tasks

## Usage

```
ix my_task
```

### Common options

All tasks have a set of common options.

##### --force

Run the task regardless of whether checkers determine the task is complete.

##### --force-all

Run the full dependency tree regardless of completion state.

##### --clean

Clean up task artifacts before running the task. This implies `--force`

##### --clean-all

Clean up all dependencies before running the dependencies. This implies 
`--force-all`.

##### --show

Display the dependency tree including which tasks pass their checks.


### Arguments and Flags

Command line arguments and flags are passed to tasks as args and kwargs to the 
task.

An example and the equivilant call in python.

```
$ ix my_task arg1 arg2 --flag --two=2
```

```python
my_task('arg1', 'arg2', flag=True, two=2)
```


## API

## Tasks

Tasks are created by extending the `task` class. Tasks must define a `name` and `execute` method.

```python
from ixian.task import Task

class MyTask(Task):
    """
    The docstring will be used as help text.
    """

    name = 'my_task'
    short_description = 'description will be shown in general help'

    def execute(self, *args, **kwargs)
        print(args, kwargs)
```

Tasks are configured by setting class properties:

* name: name used to reference task
* description: short description of task
* depends: list of dependencies
* parents: list of parent tasks
* check: list of checkers that determine if the task is complete
* clean: function to run when --clean is specified


### Checkers

Checkers determine if a task is complete or not. When a checker determines a 
task is complete it will be skipped unless `--force` or `--clean` is set. There 
are built-in checkers and support for custom checkers. 


```python
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
```

See the [Checker documentation](check.md) for more detail.


### Dependencies

Tasks may specify depend tasks that must run first. The dependency tree is 
examined and executed automatically. If a dependency's checkers indicate the
task must be run then that part of the dependency tree will be re-run.


```python
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
```

Tasks may also define parents in reverse.

```python
class Child2(Task):
    """
    This task also is a dependency of parent.
    """
    name = 'child_2'
    parent = ['parent']
    
    def execute(self, *args, **kwargs):
        print('child 2')
```


The dependency tree for a task may be viewed by the built-in help

```
ix help parent 
```

The status section will list the tree of tasks and indicate their status too.

```
STATUS
○ parent
    ○ child_1
    ○ child_2
```
