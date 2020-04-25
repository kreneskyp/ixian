import logging
import os
import re

from power_shovel.utils.filesystem import pwd
from power_shovel.utils.decorators import classproperty


logger = logging.getLogger(__name__)


class MissingConfiguration(AssertionError):
    def __init__(self, key, parent=None):
        """
        Error thrown when formatting a string but a config value is missing.
        :param parent: Key being rendered
        :param key: Key that is missing
        """
        if parent:
            msg = f"Missing config while rendering {parent}: {key}"
        else:
            msg = f"Missing config: {key}"
        super(MissingConfiguration, self).__init__(msg)


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
        value = super(Config, self).__getattribute__(key)

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

        # always format strings using the root so the full path is available
        if self.root:
            return self.root.format(value, key, **kwargs)

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
                    raise MissingConfiguration(variable, key)

        expanded.update(**kwargs)
        return value.format(**expanded)

    def resolve(self, path):
        value = self
        for key in path.split("."):
            value = getattr(value, key)
        return value

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

    # Prefix for environment variables to autoload
    ENV_PREFIX = "JT_"

    # RUN_CONTEXT - run context, by default this is the cli
    RUN_CONTEXT = "cli"

    # Local store for task runtime data.
    BUILDER_DIR = ".builder"
    BUILDER = "{PWD}/{BUILDER_DIR}"

    LOG_LEVEL = "DEBUG"
    FORMATTER = "console"
    LOGGING_CONFIG = {
        "version": 1,
        "formatters": {
            "detailed": {
                "class": "logging.Formatter",
                "format": "%(asctime)s %(levelname)-8s %(message)s",
            },
            "console": {
                "()": "power_shovel.logger.ColoredFormatter",
                "format": "%(asctime)s %(message)s",
                "log_colors": {
                    "DEBUG": "grey",
                    "INFO": "silver",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": {"color": "red", "background": "white"},
                },
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": FORMATTER,
                "level": "DEBUG",
            }
        },
        "root": {"level": "DEBUG", "handlers": [FORMATTER]},
    }

    @classproperty
    def TASKS(self):
        return TasksConfig()


class TasksConfig:
    reserved = {"reversed", "root", "__dict__"}

    def __getattribute__(self, key):
        """
        Overloaded to implement recursive lazy evaluation of properties.
        :param key: key to get
        :return: value if exists.
        """
        from power_shovel.task import TASKS

        formatted_key = key.lower()
        if formatted_key in TASKS:
            task = TASKS[formatted_key]
            return TaskConfig(task)
        else:
            return super(TasksConfig, self).__getattribute__(key)


class TaskConfig:
    def __init__(self, task):
        self.task = task

    @property
    def STATE(self):
        return self.task.state()

    @property
    def HASH(self):
        return self.task.hash()


CONFIG = Config()
