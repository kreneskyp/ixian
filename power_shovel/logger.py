import logging
from stringcolor import cs

from power_shovel.utils import color_codes as COLOR


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

        message = cs(
            message, config.get("color", DEFAULT_COLOR), config.get("background", None)
        )
        if config.get("underline", False):
            message = message.underline()
        if config.get("bold", False):
            message = message.bold()

        return str(message)
