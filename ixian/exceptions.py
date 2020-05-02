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


class AlreadyComplete(Exception):
    """
    Exception thrown when a Task executes but it's checks indicate complete.
    """


class ExecuteFailed(Exception):
    """
    Exception thrown by tasks when execute fails.
    """


class MockExit(BaseException):
    """Thrown by mock_exit to simulate exiting the process"""

    def __init__(self, code):
        self.code = code


class ModuleLoadError(Exception):
    """Error thrown when module can't be loaded"""

    pass


class InvalidClassPath(Exception):
    """Error thrown when a class path is not in the valid format"""

    pass
