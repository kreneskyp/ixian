# Copyright [2018-2020] Peter Krenesky
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import re
from importlib import import_module

from ixian.config import CONFIG
from ixian.exceptions import ModuleLoadError, InvalidClassPath
from ixian.task import Task, VirtualTarget


logger = logging.getLogger(__name__)
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
    if "name" not in MODULE_OPTIONS and not hasattr(MODULE_OPTIONS, "name"):
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
            except:  # noqa: E722
                logger.error("Error loading task: %s" % module_attribute)
                raise
