from power_shovel.config import CONFIG
from power_shovel.module import load_modules


def init():
    """Initialize with test config"""
    CONFIG.PROJECT_NAME = 'unittests'
    load_modules(
        'power_shovel.modules.core',
        'power_shovel.test.modules.test'
    )
