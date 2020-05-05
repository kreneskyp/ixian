# Modules

Ixian modules provide a way to package tasks and configuration together.

## Loading a module
Modules are loaded using `load_module`. The path should be a module containing an `OPTIONS` dict.

```python
from ixian.module import load_module

load_module("ixian.modules.core")
```

## Defining a module

create a python package and define `OPTIONS` within `__init__.py`

```python
OPTIONS = {
    "name": "MY_MODULE",
    "tasks": "path.to.my.tasks.module",
    "config": "path.to.my.config.Class",
}
```

### OPTIONS


#### Config

Set `config` to the path of your Config class. The config instance will be added to 
`CONFIG.MY_MODULE`.


#### Tasks

Set `tasks` to the path of the module containing ixian tasks. All subclasses of `Task` found in the 
module are added to the task registry.

