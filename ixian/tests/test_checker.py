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
import pytest
import uuid

from unittest.mock import Mock

from ixian import builder
from ixian.check.checker import Checker, MultiValueChecker
from ixian.modules.filesystem.file_hash import FileHash, get_flags


class MockChecker(Checker):
    def __init__(self, mock_save=True, mock_check=True, *args, **kwargs):
        self.mock_save = mock_save
        if mock_save:
            self.save = Mock()
        if mock_check:
            self.check = Mock(return_value=True)

        self.mocked_state = 1

        # random id so tests so filename is unique and tests dont leak
        self.id = uuid.uuid4()

    def state(self):
        return {"mock": self.mocked_state}

    def filename(self):
        return "mock-%s" % str(self.id)

    def clone(self):
        instance = type(self)(self.mock_save)
        instance.mocked_state = self.mocked_state
        instance.id = self.id
        if self.mock_save:
            instance.save = self.save
        return instance


class MockMultiValueChecker(MultiValueChecker):
    def __init__(self, *args):
        self.mocked_state = 100
        super(MockMultiValueChecker, self).__init__(*args)

    def state(self):
        return {"mock": self.mocked_state}


class FailingCheck(MockChecker):
    """A checker that always fails the check"""

    def __init__(self, *args, **kwargs):
        super(FailingCheck, self).__init__(*args, **kwargs)
        self.check = Mock(return_value=False)


class PassingCheck(MockChecker):
    """A checker that always passes the check"""

    pass


class TestChecker:
    """Core Checker tests"""

    @property
    def checker(self):
        return MockChecker(mock_save=False, mock_check=False)

    def test_cache(self, temp_builder):
        """Test reading and writing from hash cache"""
        checker = self.checker

        assert checker.saved_state() is None
        checker.save()
        assert checker.saved_state() == checker.state()

    def test_check_never_run(self, temp_builder):
        """Check should return False if task has never been run"""
        checker = self.checker
        assert checker.saved_state() is None
        assert not checker.check()

    def test_check_hash_match(self, temp_builder):
        """Check should return True if hash matches"""
        checker = self.checker
        checker.save()
        assert checker.check()

    def test_check_hash_mismatch(self, temp_builder):
        """Check should return False if hash does not match"""
        checker = self.checker
        checker.save()
        checker.mocked_state += 1
        assert not checker.check()


class TestMultiValueChecker(TestChecker):
    @property
    def checker(self):
        # random key so tests don't leak
        return MockMultiValueChecker(str(uuid.uuid4()))

    def test_requires_at_least_one_key(self):
        with pytest.raises(AssertionError, match="At least one key must be given"):
            MockMultiValueChecker()

    def test_clone(self):
        checker = self.checker
        clone = checker.clone()
        assert checker.keys == clone.keys
        assert checker.filename() == clone.filename()
        assert checker.file_path() == clone.file_path()
        assert checker.state() == clone.state()
        assert checker.saved_state() == clone.saved_state()


def file_hash_mock_path(path):
    import ixian.tests.mocks as mocks_module

    module_dir = os.path.dirname(os.path.realpath(mocks_module.__file__))
    return f"{module_dir}/file_hash_mocks/{path}"


class TestFileHash:
    """Tests for the FileHash checker"""

    MOCK_DIR = "dir"
    MOCK_FILE_1 = "file_1"
    MOCK_FILE_2 = "file_2"
    MOCK_FILE_1_DIFF_PERMISSIONS = "file_1_diff_permissions"
    MOCK_FILE_1_RENAMED = "file_1_renamed"
    MOCK_FILE_EMPTY = "file_2"
    MOCK_FILE_MISSING = "file_missing"

    MOCK_DIR_COPY = "dir_copy"
    MOCK_DIR_EMPTY = "dir_empty"
    MOCK_DIR_MISSING = "dir_missing"
    MOCK_DIR_DIFF_PERMISSIONS = "dir_different_permissions"

    MOCK_NESTED = "dir/level_2"

    MOCK_DIR_FILE_PERM_CHANGE = "nested_file_perm_change/level_2/file_1"
    MOCK_DIR_DIR_PERM_CHANGE = "nested_dir_perm_change/level_2"
    MOCK_DIR_FILE_RENAME = "nested_file_rename/level_2"
    MOCK_DIR_DIR_RENAME = "nested_dir_rename/level_2_renamed"
    MOCK_DIR_FILE_CHANGE = "dir_file_change"
    MOCK_DIR_FILE_EMPTY = "nested_file_empty/level_2"
    MOCK_DIR_DIR_EMPTY = "nested_dir_empty/level_2"
    MOCK_DIR_FILE_MISSING = "nested_file_missing/level_2"
    MOCK_DIR_DIR_MISSING = "nested_dir_missing/level_2"

    MOCK_NESTED_FILE_PERM_CHANGE = "nested_file_perm_change"
    MOCK_NESTED_DIR_PERM_CHANGE = "nested_dir_perm_change"
    MOCK_NESTED_FILE_RENAME = "nested_file_rename"
    MOCK_NESTED_DIR_RENAME = "nested_dir_rename"
    MOCK_NESTED_FILE_CHANGE = "nested_file_change"
    MOCK_NESTED_FILE_EMPTY = "nested_file_empty"
    MOCK_NESTED_DIR_EMPTY = "nested_dir_empty"
    MOCK_NESTED_FILE_MISSING = "nested_file_missing"
    MOCK_NESTED_DIR_MISSING = "nested_dir_missing"

    def assert_paths(self, path_1, path_2, expected):
        checker_1 = FileHash(path_1)
        checker_2 = FileHash(path_2)
        assert expected == (checker_1 == checker_2)

    # File Tests

    def test_file_hash(self):
        """Test hashing a single file"""
        path = file_hash_mock_path(self.MOCK_FILE_1)
        checker_1 = FileHash(path)
        expected = {path: "529208ab580d05f4e081d2da2cde8b80da46c39ae8f0a31d20b905057bf2f2bc"}
        assert checker_1.state() == expected

    def test_file_permission_change(self):
        """Changing permission on file changes it's hash"""
        checker_1 = FileHash(file_hash_mock_path(self.MOCK_DIR))
        checker_2 = FileHash(file_hash_mock_path(self.MOCK_FILE_1_DIFF_PERMISSIONS))
        self.assert_paths(checker_1.state(), checker_2.state(), False)

    def test_file_rename(self):
        """Testing changing a file's name"""
        # file hash
        file_1 = file_hash_mock_path(self.MOCK_FILE_1)
        file_2 = file_hash_mock_path(self.MOCK_FILE_1_RENAMED)
        # make sure flags are identical
        assert get_flags(file_1) == get_flags(file_2)
        checker_1 = FileHash(file_1)
        checker_2 = FileHash(file_2)
        assert list(checker_1.state().values())[0] == list(checker_2.state().values())[0]

    def test_file_contents_change(self):
        """Changing file contents should change file and parent dir hash"""
        checker_1 = FileHash(file_hash_mock_path(self.MOCK_FILE_1))
        checker_2 = FileHash(file_hash_mock_path(self.MOCK_FILE_2))
        self.assert_paths(checker_1.state(), checker_2.state(), False)

    def test_file_empty(self):
        """Empty file should not hash the same as a missing file"""
        checker_1 = FileHash(file_hash_mock_path(self.MOCK_FILE_1))
        checker_2 = FileHash(file_hash_mock_path(self.MOCK_FILE_EMPTY))
        self.assert_paths(checker_1.state(), checker_2.state(), False)

        checker_1 = FileHash(file_hash_mock_path(self.MOCK_FILE_EMPTY))
        checker_2 = FileHash(file_hash_mock_path(self.MOCK_FILE_MISSING))
        self.assert_paths(checker_1.state(), checker_2.state(), False)

    # =========================================================================
    # Directory tests
    # =========================================================================

    def test_dir_hash_test(self):
        """Test hashing a directory"""
        path = file_hash_mock_path(self.MOCK_DIR)
        checker_1 = FileHash(path)
        expected = {path: "f443aa643743df88ff39648d3cc04973813be298bee1c29372a9e103ad20fb47"}
        assert checker_1.state() == expected

    def test_dir_rename(self):
        """Test changing a directory's name"""
        checker_1 = FileHash(file_hash_mock_path(self.MOCK_DIR))
        checker_2 = FileHash(file_hash_mock_path(self.MOCK_DIR_COPY))
        assert list(checker_1.state().values())[0] == list(checker_2.state().values())[0]

    def test_dir_permission_change(self):
        """Changing permissions on a dir changes it's hash"""
        checker_1 = FileHash(file_hash_mock_path(self.MOCK_DIR))
        checker_2 = FileHash(file_hash_mock_path(self.MOCK_DIR_DIFF_PERMISSIONS))
        self.assert_paths(checker_1.state(), checker_2.state(), False)

    def test_dir_missing(self):
        """Hashing a missing dir"""
        checker_1 = FileHash(file_hash_mock_path(self.MOCK_DIR_EMPTY))
        checker_2 = FileHash(file_hash_mock_path(self.MOCK_DIR_MISSING))
        self.assert_paths(checker_1.state(), checker_2.state(), False)

        checker_1 = FileHash(file_hash_mock_path(self.MOCK_DIR))
        checker_2 = FileHash(file_hash_mock_path(self.MOCK_DIR_MISSING))
        self.assert_paths(checker_1.state(), checker_2.state(), False)

    def test_dir_missing_dir(self):
        """A dir missing from a dir"""
        checker_1 = FileHash(file_hash_mock_path(self.MOCK_NESTED))
        checker_2 = FileHash(file_hash_mock_path(self.MOCK_DIR_DIR_MISSING))
        self.assert_paths(checker_1.state(), checker_2.state(), False)

    def test_dir_dir_rename(self):
        """A dir containing renamed dir"""
        checker_1 = FileHash(file_hash_mock_path(self.MOCK_NESTED))
        checker_2 = FileHash(file_hash_mock_path(self.MOCK_DIR_DIR_RENAME))
        self.assert_paths(checker_1.state(), checker_2.state(), False)

    def test_dir_file_rename(self):
        """A dir containing renamed file"""
        checker_1 = FileHash(file_hash_mock_path(self.MOCK_NESTED))
        checker_2 = FileHash(file_hash_mock_path(self.MOCK_DIR_FILE_RENAME))
        self.assert_paths(checker_1.state(), checker_2.state(), False)

    def test_dir_file_change(self):
        """A dir containing renamed file"""
        checker_1 = FileHash(file_hash_mock_path(self.MOCK_NESTED))
        checker_2 = FileHash(file_hash_mock_path(self.MOCK_DIR_FILE_CHANGE))
        self.assert_paths(checker_1.state(), checker_2.state(), False)

    def test_dir_file_empty(self):
        """Missing and empty file in nested directory are not the same"""
        checker_1 = FileHash(file_hash_mock_path(self.MOCK_DIR_FILE_MISSING))
        checker_2 = FileHash(file_hash_mock_path(self.MOCK_DIR_FILE_EMPTY))
        self.assert_paths(checker_1.state(), checker_2.state(), False)

    def test_dir_dir_empty(self):
        """Missing and empty file in nested directory are not the same"""
        checker_1 = FileHash(file_hash_mock_path(self.MOCK_DIR_DIR_MISSING))
        checker_2 = FileHash(file_hash_mock_path(self.MOCK_DIR_DIR_EMPTY))
        self.assert_paths(checker_1.state(), checker_2.state(), False)

    # =========================================================================
    # Nested directory tests
    # =========================================================================

    def test_nested_file_permission_change(self):
        """changing permissions on a nested file"""
        checker_1 = FileHash(file_hash_mock_path(self.MOCK_DIR))
        checker_2 = FileHash(file_hash_mock_path(self.MOCK_NESTED_FILE_PERM_CHANGE))
        self.assert_paths(checker_1.state(), checker_2.state(), False)

    def test_nested_dir_permission_change(self):
        """changing permissions on a nested dir"""
        checker_1 = FileHash(file_hash_mock_path(self.MOCK_DIR))
        checker_2 = FileHash(file_hash_mock_path(self.MOCK_NESTED_DIR_PERM_CHANGE))
        self.assert_paths(checker_1.state(), checker_2.state(), False)

    def test_nested_file_rename(self):
        """rename file in nested dir"""
        checker_1 = FileHash(file_hash_mock_path(self.MOCK_DIR))
        checker_2 = FileHash(file_hash_mock_path(self.MOCK_NESTED_FILE_RENAME))
        self.assert_paths(checker_1.state(), checker_2.state(), False)

    def test_nested_dir_rename(self):
        """rename dir in nested dir"""
        checker_1 = FileHash(file_hash_mock_path(self.MOCK_DIR))
        checker_2 = FileHash(file_hash_mock_path(self.MOCK_NESTED_DIR_RENAME))
        self.assert_paths(checker_1.state(), checker_2.state(), False)

    def test_nested_dir_missing_file(self):
        """A nested dir that is missing a file"""
        checker_1 = FileHash(file_hash_mock_path(self.MOCK_DIR))
        checker_2 = FileHash(file_hash_mock_path(self.MOCK_NESTED_FILE_MISSING))
        self.assert_paths(checker_1.state(), checker_2.state(), False)

    def test_nested_dir_missing_dir(self):
        """A nested dir that is missing a dir"""
        checker_1 = FileHash(file_hash_mock_path(self.MOCK_DIR))
        checker_2 = FileHash(file_hash_mock_path(self.MOCK_NESTED_DIR_MISSING))
        self.assert_paths(checker_1.state(), checker_2.state(), False)
