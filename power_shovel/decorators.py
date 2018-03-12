

# =============================================================================
#  Chaining and skipping methods... very much TODO
# =============================================================================
import functools

from collections import defaultdict

from power_shovel import task


def requires():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            #cascade requirements if needed
            pass


def update_when(needs_update_func):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # TODO what if has args?
            if needs_update_func():
                return func(*args, **kwargs)
        return wrapper
    return decorator


# =============================================================================
#  Grouping targets
# =============================================================================
TARGETS = {}


class Target(object):
    def __init__(self):
        self.functions = []

    def __call__(self):
        for function in self.functions:
            function()

    def add(self, function):
        if function not in self.functions:
            self.functions.append(function)


def create_target(name):
    task(Target)
    TARGETS[name] = Target()
    return TARGETS[name]


def add_to_target(name, function):
    try:
        target = TARGETS[name]
    except KeyError:
        target = create_target(name)

    target.add(function)


def target(name):

    def decorater(function):
        add_to_target(name, function)
        return function

    return decorater
