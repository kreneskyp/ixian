# Powershovel

Powershovel is a modular task tool written in python3. It is intended to be a
replacement for Make, emulating and expanding on some of it's most useful 
features.


## Installation


TODO: Not in pypi yet but eventually...

``` 
pip install powershovel
```

## Basic Usage

#### Create a task 

Tasks are created by decorating a python function. The task should be in or 
 imported by `shovel.py` in the working directory.

```
from powershovel import task

@task()
def my_task(*args, **kwargs):
    print(args, kwargs)
```

#### Run a task

Arguments and flags are passed as `args` and `kwargs`.


```
$ shovel my_task arg1 arg2 --flag --flag=2
```


## Advanced Usage

* [Tasks](docs/tasks.md)
* [Config](docs/config.md)
* [Checks](docs/check.md)
* [Modules](docs/modules.md)
