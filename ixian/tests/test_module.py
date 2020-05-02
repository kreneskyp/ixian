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

import pytest

from ixian.config import CONFIG
from ixian.exceptions import ModuleLoadError, InvalidClassPath
from ixian.module import CLASS_PATH_PATTERN, load_module, MODULES
from ixian.runner import resolve_task


def test_class_path_pattern():
    match = CLASS_PATH_PATTERN.match("foo")
    assert match is None

    match = CLASS_PATH_PATTERN.match("foo.bar")
    assert match is not None
    assert match.groups() == ("foo", "bar")

    match = CLASS_PATH_PATTERN.match("foo.bar.xoo")
    assert match is not None
    assert match.groups() == ("foo.bar", "xoo")


@pytest.mark.usefixtures("mock_environment")
class TestModules:
    def test_load_module(self):
        """Successfully load a module"""
        from ixian.tests.mocks.modules.functional import OPTIONS
        from ixian.tests.mocks.modules.functional.tasks import TestTask
        from ixian.tests.mocks.modules.functional.config import TestConfig

        load_module("ixian.tests.mocks.modules.functional")
        assert resolve_task("test_task") is TestTask.__task__
        assert "FUNCTIONAL" in MODULES
        assert MODULES["FUNCTIONAL"] == OPTIONS
        assert type(CONFIG.FUNCTIONAL) == TestConfig

    def test_load_module_no_name(self):
        """Module name is required"""
        with pytest.raises(ModuleLoadError, match=".*: OPTIONS is missing 'name'"):
            load_module("ixian.tests.mocks.modules.no_name")

    def test_load_module_invalid_path(self):
        """If module path is bad it can't be loaded"""
        with pytest.raises(ModuleNotFoundError):
            load_module("ixian.tests.mocks.modules.does.not.exist")
        with pytest.raises(ModuleNotFoundError):
            load_module("ixian.tests.mocks.modules.invalid-module-name")

    def test_load_module_no_options(self):
        """Module options are required"""
        with pytest.raises(ModuleLoadError, match=".*: missing OPTIONS"):
            load_module("ixian.tests.mocks.modules.no_options")

    def test_load_module_no_config(self):
        """Config option is not required"""
        from ixian.tests.mocks.modules.no_config import OPTIONS
        from ixian.tests.mocks.modules.no_config.tasks import TestTask

        load_module("ixian.tests.mocks.modules.no_config")
        assert resolve_task("test_task") is TestTask.__task__
        assert "NO_CONFIG" in MODULES
        assert MODULES["NO_CONFIG"] == OPTIONS

    def test_load_module_config_path_bad_format(self):
        """Config path should be a valid classpath"""
        with pytest.raises(InvalidClassPath):
            load_module("ixian.tests.mocks.modules.config_path_invalid")

    def test_load_module_config_path_does_not_exist(self):
        """Config path should exist"""
        with pytest.raises(ModuleNotFoundError):
            load_module("ixian.tests.mocks.modules.config_path_does_not_exist")

    def test_load_module_no_tasks(self, mock_environment):
        """Module tasks are not required"""
        from ixian.tests.mocks.modules.empty_tasks_module import OPTIONS
        from ixian.tests.mocks.modules.empty_tasks_module.config import TestConfig

        load_module("ixian.tests.mocks.modules.empty_tasks_module")
        assert "EMPTY_TASKS_MODULE" in MODULES
        assert MODULES["EMPTY_TASKS_MODULE"] == OPTIONS
        assert type(CONFIG.EMPTY_TASKS_MODULE) == TestConfig

    def test_task_module_does_not_exist(self):
        """Module tasks path should exist"""
        with pytest.raises(ModuleNotFoundError):
            load_module("ixian.tests.mocks.modules.task_path_does_not_exist")

    def test_task_load_error(self):
        """An error loading a modules task is fatal"""
        with pytest.raises(Exception, match="Intentional Exception"):
            load_module("ixian.tests.mocks.modules.task_load_error")
