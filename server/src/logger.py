import logging
import warnings

from rich.console import Console
from rich.logging import RichHandler

class Logger(logging.Logger):

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.console = Console()

        rich_handler = RichHandler(
            console=self.console,
            markup=True,
            show_time=True,
            show_path=False,
            show_level=True,
        )

        formatter = logging.Formatter('%(message)s', datefmt='[%X]')
        rich_handler.setFormatter(formatter)

        self.propagate = False
        self.addHandler(rich_handler)

    def info(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.INFO):
            self._log(logging.INFO, msg, args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.DEBUG):
            self._log(logging.DEBUG, msg, args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.WARNING):
            self._log(logging.WARNING, msg, args, **kwargs)

    def error(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.ERROR):
            self._log(logging.ERROR, msg, args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.CRITICAL):
            self._log(logging.CRITICAL, msg, args, **kwargs)
