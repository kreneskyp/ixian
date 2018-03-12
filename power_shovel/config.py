import functools
import os
import re

from power_shovel.modules.filesystem.utils import pwd
from power_shovel.utils.decorators import classproperty


class MissingConfiguration(AssertionError):

    def __init__(self, value, key):
        super(MissingConfiguration, self).__init__(
            'Missing config.md while rendering %s: %s' % (value, key))


def requires_config(*properties):
    """Add assertions that make sure """
    global CONFIG

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for property in properties:
                value = getattr(CONFIG, property, None)
                if value is None:
                    raise MissingConfiguration(func.__name__, property)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def set_config(options):
    global CONFIG
    CONFIG.__dict__.update(options)


CONFIG_VARIABLE_PATTERN = re.compile(r'{(?P<var>[a-zA-Z0-9_.]+)}')


class Config(object):
    root = None
    reserved = {
        'add',
        'format',
        'reserved',
        'children',
        'root',
        '__dict__'
    }

    def __getattribute__(self, key):
        try:
            value = super(Config, self).__getattribute__(key)
        except ValueError:
            if self.root:
                return getattr(self.root, key)

        if key == 'reserved' or key in self.reserved:
            return value
        else:
            return self.format(value, key)

    def add(self, key, child_config):
        """
        Add a child config
        :param key:
        :param child_config:
        :return:
        """
        self.__dict__[key] = child_config
        child_config.root = self

    def format(self, value, key=None, **kwargs):
        """
        format variables in strings recursively.
        """
        if not isinstance(value, str):
            return value

        variables = CONFIG_VARIABLE_PATTERN.findall(value)
        expanded = {}
        for variable in variables:
            if variable not in kwargs:
                try:
                    root_key = variable.split('.')[0]
                    root = self.root if self.root else self

                    expanded[root_key] = self.format(
                        getattr(root, root_key), variable, **kwargs)
                except AttributeError:
                    raise MissingConfiguration(key, variable)

        expanded.update(**kwargs)
        return value.format(**expanded)


    # =============================================================================
    #  Base config
    # =============================================================================
    @classproperty
    def POWER_SHOVEL(cls):
        """Directory where shovel is installed"""
        import power_shovel
        return os.path.dirname(os.path.realpath(power_shovel.__file__))

    @classproperty
    def PWD(cls):
        """Directory where shovel was run from"""
        return pwd()

    PROJECT_NAME = None

    # Local store for task runtime data.
    BUILDER = '{PWD}/.builder'


CONFIG = Config()
