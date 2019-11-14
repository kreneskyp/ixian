import re
from importlib import import_module

from power_shovel import logger
from power_shovel.config import CONFIG
from power_shovel.exceptions import ModuleLoadError, InvalidClassPath
from power_shovel.task import Task, VirtualTarget

CLASS_PATH_PATTERN = re.compile(r"(?P<module_path>.*)\.(?P<classname>.+)")
MODULES = {}


def load_module(module_path):
    """
    Load module by path.

    This will load a module's config.md into CONFIG and tasks into cli.

    :param module_path: dot path to module package
    :return:
    """

    # load module and it's options
    module = import_module(module_path)
    if not hasattr(module, "OPTIONS"):
        raise ModuleLoadError(f"{module_path}: missing OPTIONS")
    MODULE_OPTIONS = getattr(module, "OPTIONS")

    # verify required options
    if "name" not in MODULE_OPTIONS:
        raise ModuleLoadError(f"{module_path}: OPTIONS is missing 'name'")

    # load config
    config_class_path = MODULE_OPTIONS.get("config", False)
    if config_class_path:
        match = CLASS_PATH_PATTERN.match(config_class_path)
        if not match:
            raise InvalidClassPath("Config classpath invalid: %s" % config_class_path)
        config_module_path, config_classname = match.groups()

        config_module = import_module(config_module_path)
        config_class = getattr(config_module, config_classname)
        CONFIG.add(MODULE_OPTIONS["name"].upper(), config_class())

    # load tasks
    tasks_module_path = MODULE_OPTIONS.get("tasks", False)
    if tasks_module_path:
        load_tasks(tasks_module_path)

    # add config to global so downstream utils/modules may use it
    MODULES[MODULE_OPTIONS["name"]] = MODULE_OPTIONS

    logger.debug("Loaded Module: {}".format(MODULE_OPTIONS["name"]))


def load_tasks(tasks_module_path):
    """Load a module with tasks in it.

    Args:
        tasks_module_path: module path as dot notation string.
    """
    tasks_module = import_module(tasks_module_path)
    for module_attribute in tasks_module.__dict__.values():
        if (
            isinstance(module_attribute, type)
            and issubclass(module_attribute, Task)
            and module_attribute not in (Task, VirtualTarget)
        ):
            try:
                module_attribute()
            except:
                logger.error("Error loading task: %s" % module_attribute)
                raise
