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

BOLD_WHITE = "\033[1m"
RED = "\033[91m"
OK_GREEN = "\033[92m"
ENDC = "\033[0m"
YELLOW = "\033[93m"
GRAY = "\033[90m"


COLOR_REFERENCE = {
    "BOLD_WHITE": BOLD_WHITE,
    "RED": RED,
    "OK_GREEN": OK_GREEN,
    "YELLOW": YELLOW,
    "GRAY": GRAY,
}


def format(txt, color):
    return f"{color}{txt}{ENDC}"


def red(txt):
    return format(txt, RED)


def green(txt):
    return format(txt, OK_GREEN)


def yellow(txt):
    return format(txt, YELLOW)


def gray(txt):
    return format(txt, GRAY)


def bold_white(txt):
    return format(txt, BOLD_WHITE)
