from enum import Enum


class LogLevels(Enum):
    NONE = -1
    ERROR = 0
    WARN = 1
    INFO = 2
    DEBUG = 3


__LEVEL = LogLevels.ERROR


def set_level(level):
    global __LEVEL
    __LEVEL = level


def error(txt):
    if __LEVEL.value >= LogLevels.ERROR.value:
        print(txt)


def warn(txt):
    if __LEVEL.value >= LogLevels.WARN.value:
        print(txt)


def info(txt):
    if __LEVEL.value >= LogLevels.INFO.value:
        print(txt)


def debug(txt):
    if __LEVEL.value >= LogLevels.DEBUG.value:
        print(txt)


__all__ = [
    LogLevels,
    set_level,
    error,
    warn,
    info,
    debug
]
