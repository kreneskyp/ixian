import hashlib
import json

import os

from power_shovel.config import CONFIG
from power_shovel.modules.filesystem.utils import mkdir


def hash_object(obj):
    """deterministically hash a dict."""
    hash = hashlib.sha256()
    hash.update(json.dumps(obj, sort_keys=True).encode('utf-8'))
    return hash.hexdigest()


class Checker(object):
    """
    Checkers determine whether a task should run or be skipped. Tasks may have
    zero or more checkers that run before it is executed. The task will skip
    when the checker indicates the task is already compete.

    Each checker should implement the `data` method which returns an object
    that represents the state being checked. The state object is serialized and
    saved after successful runs. The current state is compared against this to
    determine whether the task should run.
    """

    def check(self):
        return self.state() == self.saved_state()

    # TODO optimize to avoid repeated state calculation
    def state(self):
        """
        State being considered as part of this check. State is expected to be
        a dict of properties and their values. State must be json serializable
        and sorted.

        State values may be any type of json serializable object. For example,
        a file_hasher would use a hash of the file.

        The set of keys in a state object should be idempotent regardless of
        state.

        :return: state dict
        """
        raise NotImplementedError

    def saved_state(self):
        """
        Retrieved saved state, if any.  If task has not been run successfully
        it's state will be None.
        :return: state object
        """
        file_path = self.file_path()
        if os.path.exists(file_path):
            with open(file_path) as file:
                return json.loads(file.read())
        else:
            return None

    def file_path(self):
        """Path where state file can be found.

        :return: path
        """
        return CONFIG.format(
            '{BUILDER}/{file_name}',
            file_name=self.filename())

    def filename(self):
        """
        Generate a filename that is a deterministic representation of the
        dependencies being checked.
        """
        raise NotImplementedError

    def save(self):
        mkdir(CONFIG.format('{BUILDER}/checks/'))
        state = self.state()
        with open(self.file_path(), 'w') as file:
            file.write(json.dumps(state))

    def clone(self):
        raise NotImplementedError


class SingleKeyChecker(Checker):
    """Checker that checks a single key"""

    def __init__(self, key):
        self.key = key

    def filename(self):
        """"Generate file path using keys of the data dict."""
        return hashlib.sha256(self.key).hexdigest()


class MultiValueChecker(Checker):
    """Checker that checks multiple keys."""

    def __init__(self, *keys):
        self._keys = keys

    @property
    def keys(self):
        """list of keys saved in this instance"""
        return self._keys

    def filename(self):
        """"Generate file path using keys of the data dict."""
        return hash_object(self.keys)

    def clone(self):
        return type(self)(self.keys)


