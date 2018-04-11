# Configuration

Powershovel includes a configuration system to configure builds. Configuration
is modular so that modules may provide options without additionally setup.

## Using Config

Configuration is used by importing `CONFIG`. `CONFIG` returns an a shared 
instance of `Config`. Tasks and other code can reference this instance directly
to simplify module setup.

```python
from power_shovel.config import CONFIG

print(CONFIG.POWER_SHOVEL)
```

Other config classes may be added as children of a config instance. Modules add
to `CONFIG`. 


## Config classes

Configuration is added through `Config` subclasses. Config options may be added
as static variables or with properties. Properties allow for caching and 
runtime calculations. 

```python
from power_shovel.config import Config

class MyConfig(Config):
    
    ONE = 1
    
    @property
    def PLUS_ONE(self):
        return self.ONE + 1
```

Configuration is loaded into the `CONFIG` instance.  This may be done manually
or as part of a [module](modules.md).

```python

from power_shovel.config import CONFIG
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

String configuration options may include config variables. The variables are 
recursively expanded when returned by `CONFIG`.  This allows configuration to
be defined relatively.

```python

from power_shovel.config import Config

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

### Formatting strings with config values

Config instances can be used to format strings too. This 

```python
# format a string
CONFIG.format('{MY_CONFIG.ROOT}/example/path')

# add kwargs to add extra format keys
CONFIG.format('{MY_CONFIG.ROOT}/{foo}', foo='extra_value')
```

## Built in Config

The properties are built into the base Config class and `CONFIG`.

#### POWER_SHOVEL
The directory where power_shovel is installed.

#### PWD
The present working directory. This is the directory power_shovel was run from.

#### PROJECT_NAME
The name of the project. The default value is `None`, this should be set by
the project during setup.

#### BUILDER
The local store used by power_shovel. This is where state and any other files
used during builds should persist. Defaults to `{PWD}/.builder`.
