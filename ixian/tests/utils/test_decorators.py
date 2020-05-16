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

from unittest import mock

from ixian.utils.decorators import classproperty, cached_property


class Foo:
    _bar = "success"

    @classproperty
    def bar(self):
        return "success"

    @bar.setter
    def bar(self, value):
        self._bar = value


class TestClassProperty:
    def test_get_class(self):
        assert Foo.bar == "success"

    def test_get_instance(self):
        assert Foo().bar == "success"

    def test_set_class(self):
        Foo.bar = "new value"
        assert Foo.bar == "new value"

    def test_set_instance(self):
        foo = Foo()
        foo.bar = "new value"
        assert foo.bar == "new value"


def test_cached_property():
    func = mock.Mock(return_value=1)

    class Foo:
        @cached_property
        def bar(self):
            return func()

    # first access should call underlying method
    foo = Foo()
    assert foo.bar == 1
    func.assert_called_with()
    func.reset_mock()

    # subsequent access should use cache
    assert foo.bar == 1
    func.assert_not_called()
