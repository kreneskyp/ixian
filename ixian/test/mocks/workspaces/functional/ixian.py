from ixian.config import CONFIG
from ixian.module import load_module


def init():
    """Initialize with test config"""
    CONFIG.PROJECT_NAME = "unittests"
    load_module("ixian.modules.core")
    load_module("ixian.test.mocks.modules.functional")
