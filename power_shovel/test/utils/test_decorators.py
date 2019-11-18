import pytest
from unittest import mock

from power_shovel.utils.decorators import classproperty, cached_property


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
