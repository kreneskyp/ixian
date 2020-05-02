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

import io

from ixian.task import Task, VirtualTarget


class Lint(VirtualTarget):
    """Virtual target for linting project."""

    name = "lint"
    category = "testing"
    short_description = "Run all linting tasks."


class Test(VirtualTarget):
    """Virtual target for running all tests."""

    name = "test"
    category = "testing"
    short_description = "Run all testing tasks."


# =============================================================================
#  Teardown
# =============================================================================


class Clean(VirtualTarget):
    """Virtual target for cleaning the project."""

    name = "clean"
    category = "build"
    short_description = "Run all clean tasks."


class Help(Task):
    """
    Ixian internal help. Displays either internal help or a task's help.
    """

    name = "help"
    short_description = "This help message or help <task> for task help"
    contexts = True

    def execute(self, task_name=None):
        from ixian import runner

        if task_name:
            subtask = runner.resolve_task(task_name)
            buffer = io.StringIO()
            subtask.render_help(buffer)
            print(buffer.getvalue())
            buffer.close()
        else:
            parser = runner.get_parser()
            parser.print_help()
        return 0
