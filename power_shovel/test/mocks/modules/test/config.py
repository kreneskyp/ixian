from power_shovel.config import Config
from power_shovel.utils.decorators import classproperty


class TestConfig(Config):
    @classproperty
    def DYNAMIC(cls):
        """A dynamic configuration using a class property"""
        return "dynamic"

    NUMBER = 1
    LIST = [1, 2]
    DICT = {"a": 1, "b": 2}
    STRING = "string"
    REFERENCE = "{TEST.STRING}/{TEST.NUMBER}"
    NESTED_REFERENCE = "{TEST.REFERENCE}"
