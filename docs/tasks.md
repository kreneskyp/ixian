# Tasks

## Usage

```
shovel my_task
```

### Common options

All tasks have a set of common options.

##### --force

Run the task regardless of whether checkers determine the task is complete.

##### --force-all

Run the full dependency tree regardless of checkers.

##### --clean [TODO]

Clean up task artifacts before running it.

##### --clean-all [TODO]

Clean up all dependencies before running them.

##### --show [TODO]

Display the dependency tree including which tasks pass their checks.



### Arguments and Flags

Command line arguments and flags are passed to tasks as args and kwargs to the 
task.

An example and the equivilant call in python.

```
$ shovel my_task arg1 arg2 --flag --two=2
```

```python
my_task('arg1', 'arg2', flag=True, two=2)
```


## API

## Task Decorator

Tasks are created with the `@Task` decorator. This includes a number of 


### Checkers

Checkers determine if a task is complete or not. When a checker determines a 
task is complete it will be skipped unless `--force` or `--clean` is set. There 
are built-in checkers and support for custom checkers. 

Checkers are specified with the decorator. 

```python
from power_shovel import task
from power_shovel.modules.filesystem.file_hash import FileHash

@task(checkers=[
    FileHash('/input_file'), 
    FileHash('/output_file')])
def my_task():
    # This task will only run if there if the files are modified or removed.
    pass
```

See the [Checker documentation]() for more detail.


### Dependencies

Tasks may specify depend tasks that must run first. The dependency tree is 
examined and executed automatically. If a dependency's checkers indicate the
task must be run then that part of the dependency tree will be re-run.


```python
from power_shovel import task

@task()
def my_task():
    pass


@task(dependencies=[my_task])
def my_other_task():
    # this task will execute `my_task` first.
    pass
```

The dependency tree for a task may be viewed with `--show` when executing the
task.
