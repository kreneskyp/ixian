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
import logging
import os

from ixian.config import CONFIG
from ixian.utils.filesystem import mkdir, empty_dir, write_file, read_file


logger = logging.getLogger(__name__)


def get_path(relative_path):
    return f"{CONFIG.BUILDER}/{relative_path}"


def write(path: str, data: str):
    """
    Shortcut for writing files to BUILDER. Paths is relative to builder.
    """
    full_path = get_path(path)
    write_file(full_path, data)
    logger.debug(f"Builder wrote to {path}")
    print(f"Builder wrote to {path}")


def read(path: str):
    """
    Shortcut or reading file from BUILDER. Path is relative to builder.
    """
    full_path = get_path(path)
    return read_file(full_path)


def exists(path: str):
    """
    Returns True if path exists in BUILDER
    """
    full_path = get_path(path)
    return os.path.exists(full_path)


def reset():
    """
    Delete all files in BUILDER
    """
    empty_dir(CONFIG.BUILDER)
