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

import hashlib
import json

import os

from ixian.config import CONFIG
from ixian.utils.filesystem import mkdir


def hash_object(obj):
    """deterministically hash a dict."""
    hash = hashlib.sha256()
    hash.update(json.dumps(obj, sort_keys=True).encode("utf-8"))
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

    contribute_to_task_state = True

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

    def hash(self):
        return hash_object(self.state())

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
        return CONFIG.format("{BUILDER}/checks/{file_name}", file_name=self.filename())

    def filename(self):
        """
        Generate a filename that is a deterministic representation of the
        dependencies being checked.
        """
        raise NotImplementedError

    def save(self):
        mkdir(CONFIG.format("{BUILDER}/checks/"))
        state = self.state()
        with open(self.file_path(), "w") as file:
            file.write(json.dumps(state))

    def clone(self):
        raise NotImplementedError


class MultiValueChecker(Checker):
    """Checker that checks multiple keys."""

    def __init__(self, *keys):
        assert len(keys) != 0, "At least one key must be given"
        self._keys = keys

    @property
    def keys(self):
        """list of keys saved in this instance"""
        return [CONFIG.format(key) for key in self._keys]

    def filename(self):
        """"Generate file path using keys of the data dict."""
        return hash_object(self.keys)

    def clone(self):
        return type(self)(*self._keys)
