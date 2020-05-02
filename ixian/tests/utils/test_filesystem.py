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
    assert filesystem.pwd() == "/opt/ixian"
