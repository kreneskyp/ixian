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
import shutil


logger = logging.getLogger(__name__)


def mkdir(path: str) -> None:
    """Make directories in path if they don't exist"""
    if not os.path.exists(path):
        os.makedirs(path)


def pwd() -> str:
    """Return working directory"""
    return os.getcwd()


def rmdir(path: str) -> None:
    shutil.rmtree(path)


def empty_dir(path: str) -> None:
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logger.error("Failed to delete %s: %s" % (file_path, e))


def write_file(path: str, data: str):
    """
    Write a file to the filesystem, creating any missing directories in the path.
    """
    dir = os.path.dirname(path)
    mkdir(dir)

    with open(path, "w") as file:
        file.write(data)

    print("wrote to: ", path)


def read_file(path: str):
    """
    Read a file from the filesystem.
    """
    with open(path, "r") as file:
        data = file.read()
    return data
