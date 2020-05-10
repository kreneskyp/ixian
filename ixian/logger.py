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
from stringcolor import cs


DEFAULT_COLORS = {
    "DEBUG": "white",
    "INFO": "white",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "red",
}


DEFAULT_COLOR = "silver"


class ColoredFormatter(logging.Formatter):
    """
    A formatter that allows colors to be placed in the format string.

    Intended to help in creating more readable logging output.
    """

    def __init__(self, fmt=None, datefmt=None, style="%", log_colors=None):
        self.log_colors = log_colors or DEFAULT_COLORS
        super(ColoredFormatter, self).__init__(fmt=fmt, datefmt=datefmt, style=style)

    def format(self, record):
        message = logging.Formatter.format(self, record)

        config = self.log_colors.get(record.levelname, DEFAULT_COLOR)
        if isinstance(config, str):
            config = {
                "color": config,
                "background": None,
                "underline": False,
                "bold": False,
            }

        elif not isinstance(config, dict):
            raise ValueError("color setting must be a string or dict")

        message = cs(message, config.get("color", DEFAULT_COLOR), config.get("background", None))
        if config.get("underline", False):
            message = message.underline()
        if config.get("bold", False):
            message = message.bold()

        return str(message)
