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

from ixian.utils import color_codes


@pytest.fixture(params=list(color_codes.COLOR_REFERENCE.items()))
def color(request):
    yield request.param


@pytest.fixture(
    params=[
        color_codes.red,
        color_codes.green,
        color_codes.yellow,
        color_codes.gray,
        color_codes.bold_white,
    ]
)
def color_method(request):
    yield request.param


class TestColorCodes:
    """Test that all color codes render"""

    def test_colors(self, snapshot, color):
        """Test that all colors may be printed"""
        name, color = color
        snapshot.assert_match(color_codes.format("testing", color), name)

    def test_color_methods(self, snapshot, color_method):
        snapshot.assert_match(color_method("testing"))
