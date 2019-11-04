import functools
import os
import re

from power_shovel.modules.filesystem.utils import pwd
from power_shovel.utils.decorators import classproperty


class MissingConfiguration(AssertionError):
    def __init__(self, value, key):
        super(MissingConfiguration, self).__init__(
            "Missing config while rendering %s: %s" % (value, key)
        )


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


CONFIG_VARIABLE_PATTERN = re.compile(r"{(?P<var>[a-zA-Z0-9_.]+)}")


class Config(object):
    root = None
    reserved = {"add", "format", "reserved", "children", "root", "__dict__"}

    def __getattribute__(self, key):
        """
        Overloaded to implement recursive lazy evaluation of properties.
        :param key: key to get
        :return: value if exists.
        """
        try:
            value = super(Config, self).__getattribute__(key)
        except ValueError:
            if self.root:
                return getattr(self.root, key)

        if key == "reserved" or key in self.reserved:
            return value
        else:
            return self.format(value, key)

    def add(self, key, child_config):
        """
        Add a child config
        :param key: Key to add child config as. e.g. "PYTHON"
        :param child_config: config to add.
        """
        self.__dict__[key] = child_config
        child_config.root = self

    def format(self, value, key=None, **kwargs):
        """
        Format strings using CONFIG object.

        This method uses python's built-in `str.format()` method. All root
        properties in CONFIG are passed in as kwargs. The properties lazy
        evaluate and recursively expand.

        Example:
            "{HOST}:{PORT}" may be formatted "0.0.0.0:8000"

        :param value: string to format
        :param key: TODO: is this needed?
        :param **kwargs: additional kwargs to format
        """
        if not isinstance(value, str):
            return value

        variables = CONFIG_VARIABLE_PATTERN.findall(value)
        expanded = {}
        for variable in variables:
            if variable not in kwargs:
                try:
                    root_key = variable.split(".")[0]
                    root = self.root if self.root else self

                    expanded[root_key] = self.format(
                        getattr(root, root_key), variable, **kwargs
                    )
                except AttributeError:
                    raise MissingConfiguration(key, variable)

        expanded.update(**kwargs)
        return value.format(**expanded)

    # =========================================================================
    #  Base config
    # =========================================================================
    @classproperty
    def POWER_SHOVEL(cls):
        """Directory where power_shovel is installed"""
        import power_shovel

        return os.path.dirname(os.path.realpath(power_shovel.__file__))

    @classproperty
    def PWD(cls):
        """Directory where shovel was run from"""
        return pwd()

    PROJECT_NAME = None

    # ENV - build environment PRODUCTION or DEV
    ENV = "DEV"

    # Local store for task runtime data.
    BUILDER_DIR = ".builder"
    BUILDER = "{PWD}/{BUILDER_DIR}"


CONFIG = Config()
