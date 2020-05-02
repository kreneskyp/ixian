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

from ixian.config import Config
from ixian.utils.decorators import classproperty


class TestConfig(Config):
    @classproperty
    def DYNAMIC(cls):
        """A dynamic configuration using a class property"""
        return "dynamic"

    NUMBER = 1
    LIST = [1, 2]
    DICT = {"a": 1, "b": 2}
    STRING = "string"
    REFERENCE = "{TEST.STRING}/{TEST.NUMBER}"
    NESTED_REFERENCE = "{TEST.REFERENCE}"
