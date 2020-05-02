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

import uuid
from unittest import mock

from ixian.check.checker import Checker


class MockChecker(Checker):
    def __init__(self, name, mock_save=True, mock_check=True, *args, **kwargs):
        self.name = name
        self.mock_save = mock_save
        self.mock_check = mock_check
        if mock_save:
            self.save = mock.Mock(name=f"{name}-save")
        if mock_check:
            self.check = mock.Mock(name=f"{name}-check", return_value=True)

        self.mocked_state = 1
        self.id = uuid.uuid4()

    def state(self):
        return {"mock": self.mocked_state}

    def filename(self):
        return "mock-%s" % str(self.id)

    def clone(self):
        instance = type(self)(self.mock_save, self.mock_check)
        instance.mocked_state = self.mocked_state
        instance.id = self.id
        if self.mock_save:
            instance.save = self.save
        if self.mock_check:
            instance.check = self.check
        return instance


class FailingCheck(MockChecker):
    """A checker that always fails the check"""

    def __init__(self, *args, **kwargs):
        super(FailingCheck, self).__init__(*args, **kwargs)
        self.check = mock.Mock(return_value=False)


class PassingCheck(MockChecker):
    """A checker that always passes the check"""

    pass
