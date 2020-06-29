import os

import pytest

from ixian.config import CONFIG
from ixian import builder
from ixian.utils import filesystem


class TestTempBuilder:
    """
    Some sanity tests for temp_builder fixture
    """

    def test_temp_builder(self, temp_builder):
        """
        basic sanity test
        """
        path = "TestTempBuilder.test"
        assert not builder.exists(path), "file should not exist yet"
        builder.write(path, "test file")
        assert builder.exists(path), "file should exist now"

    @pytest.mark.parametrize("i", [1, 2])
    def test_temp_builder_leak_test(self, i, temp_builder):
        """
        Test that builds are not leaking. Both iterations of the test write to the same file. The
        first test should clean the file. The 2nd test may only pass if the file does not exist.

        Note that this only proves that one of the following are working:
        - temp_builder has a random directory
        - the files were cleaned up

        Ideally, both would happen but the main concern is that tasks don't leak.
        """
        path = "TestTempBuilder.leak_test"
        assert not builder.exists(path), "file should not exist yet"
        builder.write(path, "This file should be cleaned up at the end of the test")
        assert builder.exists(path), "file should exist now"


class TestReadWrite:
    def assert_read_write_file(self, path, data):
        """
        Assert that file can be written and read back from builder
        """
        assert not builder.exists(path)
        builder.write(path, data)
        assert builder.exists(path)
        assert builder.read(path) == data

    def test_path_exists(self, temp_builder):
        """
        Test writing to file when the directories already exist
        """
        path = f"builder.TestReadWrite/test_path_exists"
        file = f"{path}/file"
        filesystem.mkdir(builder.get_path(path))
        assert builder.exists(path)
        self.assert_read_write_file(file, "test_path_exists")

    def test_path_doesnt_exist(self, temp_builder):
        """
        Test writing to file when the directories do not exist
        """
        path = f"TestReadWrite/test_path_doesnt_exist"
        file = f"{path}/file"
        assert not builder.exists(path)
        self.assert_read_write_file(file, "test_path_doesnt_exist")


def test_reset(temp_builder):
    """
    Test resetting (clearing) the builder directory
    """
    path = "reset_test"
    builder.write(path, "reset test")
    assert builder.exists(path)
    builder.reset()
    assert not builder.exists(path)
