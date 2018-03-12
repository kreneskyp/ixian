import re
from importlib import import_module

from power_shovel.config import CONFIG

CLASS_PATH_PATTERN = re.compile(r'(?P<module_path>.*)\.(?P<classname>.+)')


def load_module(module_path):
    """
    Load module by path.

    This will load a module's config.md into CONFIG and tasks into cli.

    :param module_path: dot path to module package
    :return:
    """

    module = import_module(module_path)
    try:
        MODULE_CONFIG = getattr(module, 'MODULE_CONFIG')
    except AssertionError:
        MODULE_CONFIG = {}

    # load config
    config_class_path = MODULE_CONFIG.get('config', False)
    if config_class_path:
        match = CLASS_PATH_PATTERN.match(config_class_path)
        if not match:
            raise Exception('Config classpath invalid: %s' % config_class_path)
        config_module_path, config_classname = match.groups()

        config_module = import_module(config_module_path)
        config_class = getattr(config_module, config_classname)
        CONFIG.add(MODULE_CONFIG['name'].upper(), config_class())

    # load tasks
    tasks_module_path = MODULE_CONFIG.get('tasks', False)
    if tasks_module_path:
        import_module(tasks_module_path)

    # TODO this is a docker specific feature. Should probably make a loading
    # hook system so this power_shovel can remain agnostic.
    # load docker environment
    CONFIG.DOCKER.VOLUMES.extend(MODULE_CONFIG.get('volumes', []))
    CONFIG.DOCKER.ENV.update(MODULE_CONFIG.get('environment', {}))
    CONFIG.DOCKER.DEV_VOLUMES.extend(MODULE_CONFIG.get('dev_volumes', []))
    CONFIG.DOCKER.DEV_ENV.update(MODULE_CONFIG.get('dev_environment', {}))


def load_modules(*module_paths):
    for module_path in module_paths:
        load_module(module_path)
