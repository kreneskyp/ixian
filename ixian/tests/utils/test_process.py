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

from ixian.exceptions import ExecuteFailed
from ixian.utils.process import (
    raise_for_status,
    get_dev_uid,
    get_dev_gid,
    execute,
)


class TestRaiseForStatus:
    def test_zero(self):
        """zero is the unix standard for a successful process. No error should be raised."""
        raise_for_status(0)

    def test_error(self):
        """Error codes should raise ExecuteFailed"""
        for code in [-2, -1, 1, 2]:
            with pytest.raises(ExecuteFailed):
                raise_for_status(code)


class TestExecute:
    """Tests for `execute` helper that is used to run shell commands"""

    def test_success(self):
        """Test a process returning successfully"""
        return_code = execute("ls")
        assert return_code == 0

    def test_error(self):
        """Test a process returning a nonzero code"""
        return_code = execute("false")
        assert return_code == 1

    def test_command_formatting(self):
        """Variables in the command are expanded before being executed"""
        return_code = execute("echo this is the working directory: {PWD}")
        assert return_code == 0

    def test_command_multiple_args(self):
        """command may be a string with space separated arguments"""
        return_code = execute("echo this command has args")
        assert return_code == 0

    def test_silent(self, mock_logger):
        """when silent, command is not echoed by the logger"""
        return_code = execute("ls", silent=True)
        assert return_code == 0
        mock_logger.info.assert_not_called()

        # Test with silent=False to sanity check
        return_code = execute("ls", silent=False)
        assert return_code == 0
        mock_logger.info.called_with("ls")


def test_get_dev_uid():
    ix_test_context = os.getenv("IX_TEST_CONTEXT", "UNKNOWN")
    if ix_test_context == "LOCAL":
        expected = 0
    else:
        # uid used by github actions
        expected = 1001
    assert get_dev_uid() == expected


def test_get_dev_gid():
    ix_test_context = os.getenv("IX_TEST_CONTEXT", "UNKNOWN")
    if ix_test_context == "LOCAL":
        expected = 0
    else:
        # gid used by github actions
        expected = 116
    assert get_dev_gid() == expected
