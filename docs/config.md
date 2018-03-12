# Configuration

Powershovel includes a configuration system to configure builds. Configuration
is modular so that modules may provide options without additionally setup.

Configuration is used by importing `CONFIG`.

```python
from power_shovel.config import CONFIG

print(CONFIG.POWER_SHOVEL)
```


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
or as part of a module (TODO: Link to module docs)

```python

from power_shovel.config import CONFIG
CONFIG.add('MY_CONFIG', MyConfig)
print(CONFIG.MY_CONFIG.ONE)
```


## Variable Replacement

String configuration options may include config variables. The variables are 
recursively expanded when returned by `CONFIG`.  This allows configuration to
be defined relatively.

```python

class MyConfig(Config):
    ROOT = '/my/directory/' 
    
    # Relative reference to property in this class.
    TWO = '{ROOT}/my_file'
    
    # Absolute reference to CONFIG value. This may be used to reference 
    # variables defined by other classes, but requires the absolute path they
    # are mapped to.
    THREE = '{MY_CONFIG.ROOT}/my_file'
```

If a config option isn't available then a `MissingConfiguration` error will be
raised indicating the variable that couldn't be rendered and the variable it
requires.
