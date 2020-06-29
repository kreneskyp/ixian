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

import os
import shutil

from ixian import builder
from ixian.config import CONFIG

from ixian.utils import filesystem


def test_mkdir():
    path = "/tmp/mkdir_test/foo"
    if os.path.exists(path):
        shutil.rmtree(path)
    assert not os.path.exists(path)

    # test creating the directories
    filesystem.mkdir(path)
    assert os.path.exists(path)

    # calling it a second time should not raise an error
    filesystem.mkdir(path)
    assert os.path.exists(path)


def test_pwd():
    assert filesystem.pwd() == "/home/runner/work/ixian/ixian"


class TestWritePath:
    def assert_read_write_file(self, path, data):
        """
        Assert that file can be written and read back from filesystem
        """
        full_path = builder.get_path(path)
        assert not builder.exists(path)
        filesystem.write_file(full_path, data)
        assert builder.exists(path)
        assert filesystem.read_file(full_path) == data

    def test_path_exists(self, temp_builder):
        """
        Test writing to file when the directories already exist
        """
        path = f"filesystem.TestReadWrite/test_path_exists"
        file = f"{path}/file"
        full_path = builder.get_path(path)
        filesystem.mkdir(full_path)
        assert builder.exists(path)
        self.assert_read_write_file(file, "test_path_exists")

    def test_path_doesnt_exist(self, temp_builder):
        """
        Test writing to file when the directories do not exist
        """
        path = f"filesystem.TestReadWrite/test_path_doesnt_exist"
        file = f"{path}/file"
        assert not builder.exists(path)
        self.assert_read_write_file(file, "test_path_doesnt_exist")
