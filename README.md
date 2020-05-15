![test](https://github.com/kreneskyp/ixian/workflows/test/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/docs/badge/?version=latest)](https://ixian.readthedocs.io/en/latest/)

# Ixian

Ixian is a modular task tool written in python3. It is intended to be a
replacement for Make, emulating and expanding on some of it's most useful 
features.

## Installation

``` 
pip install ixian
```

## Setup

Create an `ixian.py` file where you intend to call `ix` from. Optionally set `IXIAN_CONFIG` to tell
ixian where to find it.

Within that file create an `init` method that loads modules and configures settings.

```python
from ixian.config import CONFIG
from ixian.module import load_module


def init():
    # Load modules which contain tasks
    load_module('ixian.modules.core')

    # Update settings
    CONFIG.PROJECT_NAME = 'testing'
```

## Create a task 

Tasks are created by extending the task class. 

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

## Run a task
The task may then be called using the `ix` runner. 

```
ix my_task
```

Args passed to the runner are passed to the task as `args`
```
ix my_task arg1 arg2
```

## Builtin help
A list of available commands is available by calling `ix` or `ix --help`.
 
Access built-in help for any task by calling `ix help my_task`. Builtin help should display how to
use the task, enumerate any relevent environment variables, and display the status of any checks.



