from power_shovel.config import CONFIG
from power_shovel.module import load_module


def init():
    """Initialize with test config"""
    CONFIG.PROJECT_NAME = "unittests"
    load_module("power_shovel.modules.core")
    load_module("power_shovel.test.mocks.modules.functional")
