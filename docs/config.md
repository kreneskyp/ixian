# Configuration

Ixian includes a configuration system to configure builds. Configuration
is modular so that modules may provide options without additionally setup.

## Using Config

Configuration is used by importing `CONFIG`. `CONFIG` returns an a shared
instance of `Config`. Tasks and other code can reference this instance directly
to simplify module setup.

```python
from ixian.config import CONFIG

print(CONFIG.IXIAN)
```

Other config classes may be added as children of a config instance. Modules add
to `CONFIG`.


## Config classes

Configuration is added through `Config` subclasses. Config options may be added
as static variables or with properties. Properties allow for caching and
runtime calculations.

```python
from ixian.config import Config

class MyConfig(Config):
    
    ONE = 1
    
    @property
    def PLUS_ONE(self):
        return self.ONE + 1
```

Configuration is loaded into the `CONFIG` instance.  This may be done manually
or as part of a [module](modules.md).

```python

from ixian.config import CONFIG
CONFIG.add('MY_CONFIG', MyConfig)
print(CONFIG.MY_CONFIG.ONE)
```

### Adding config classes to CONFIG

Config subclasses may be added as children. The child config is added as a
property under the key.

```python
CONFIG.add('MY_CONFIG', MyConfig())

print(CONFIG.MY_CONFIG)
```


## Variable Replacement

String configuration options may include config variables wrapped in curly braces. The variables
are recursively expanded when returned by `CONFIG`.  This allows configuration to be defined 
relatively.

```python

from ixian.config import Config

class MyConfig(Config):
    ROOT = '/my/directory/' 
    
    # Relative reference to property in this class.
    TWO = '{ROOT}/my_file'
    
    # Absolute reference to CONFIG value. This may be used to reference 
    # variables defined by other classes, but requires the absolute path they
    # are mapped to. Use dot notation to traverse to child properties.
    THREE = '{MY_CONFIG.ROOT}/my_file'
```

If a config option isn't available then a `MissingConfiguration` error will be
raised indicating the variable that couldn't be rendered and the variable it
requires.

Ixian formatting is an extension of `string.format`. Because values may be set at runtime via
configuration and environment variables it cannot arbitrary execution like f-strings do.

### Formatting strings with config values

Config instances can be used to format strings too.

```python
# format a string
CONFIG.format('{MY_CONFIG.ROOT}/example/path')

# add kwargs to add extra format keys
CONFIG.format('{MY_CONFIG.ROOT}/{foo}', foo='extra_value')
```

### Resolve a value

Values can be resolved from strings.

```python
CONFIG.resolve('MY_CONFIG.ROOT')
```

If the value is a string it will be formatted.


```python
CONFIG.MY_CONFIG.FOO = 'bar'
CONFIG.MY_CONFIG.ROOT = 'root/{MY_CONFIG.FOO}'

# returns "root/bar"
CONFIG.resolve('MY_CONFIG.ROOT')
```

If the value is a list, dict or other type that nests other values, those values will not be
formatted.

```python
CONFIG.MY_CONFIG.VALUE = 'value'
CONFIG.MY_CONFIG.FOO = ['{value}']
CONFIG.MY_CONFIG.BAR = {'{FOO}': '{VALUE}'}

# returns list as is
CONFIG.resolve('MY_CONFIG.FOO')

# returns dict as is
CONFIG.resolve('MY_CONFIG.FOO')
```


## Built in Config

The properties are built into the base Config class and `CONFIG`.

#### IXIAN
The directory where ixian is installed.

#### PWD
The present working directory. This is the directory ixian was run from.

#### PROJECT_NAME
The name of the project. The default value is `None`, this should be set by
the project during setup.

#### ENV
The environmnet type that is running. `DEV` or `PRODUCTION`. default is `DEV`

#### ENV_PREFIX
Ixian updates config from environment variables. Environment variables starting with `ENV_PREFIX`
are parsed and loaded into matching config paths.

Default value is `JT_`

Double underscores are treated as dots. `JT_CORE__PROJECT_NAME` is resolved to `CORE.PROJECT_NAME`
The value will be parsed and replace the existing value.

#### RUN_CONTEXT TODO
The context in which `ix` was run. Contexts are used to filter tasks that are loaded. This can be
used to share a single ixian config file for different uses like cli, ci/cd, or in containers.

#### BUILDER_DIR


#### BUILDER
The local store used by ixian. This is where state and any other files
used during builds should persist. Defaults to `{PWD}/.builder`.

#### LOG_LEVEL
Log level to display

#### LOG_FORMATTER
Formatter name to use. Will select a formatter defined in `LOGGING_CONFIG['formatters']`. Defaults 
to `console`.

#### LOGGING_CONFIG
A python logging config dict.

#### TASKS
A reference to all tasks registered with ixian. Upper or lower case names may be used with this
property.

```python
# Both are equivalent
CONFIG.TASKS.my_task
CONFIG.TASKS.MY_TASK
```