from rich.console import Console
from rich.logging import RichHandler
from rich.pretty import pretty_repr
import logging
import warnings

class Logger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self, level=logging.DEBUG):
        if not hasattr(self, "logger"):
            self.console = Console()
            self.logger = logging.getLogger("webscraper")
            self.logger.setLevel(level)

            rich_handler = RichHandler(console=self.console, markup=True, show_time=True, show_path=False, show_level=True, level=logging.DEBUG)
            formatter = logging.Formatter("%(message)s", datefmt="[%X]")
            rich_handler.setFormatter(formatter)

            self.logger.propagate = False
            rich_handler.setLevel(level)
            self.logger.addHandler(rich_handler)
            warnings.filterwarnings("ignore")

    def info(self, class_name, message):
        self.logger.info(f'[bold green][{class_name}][/]: {message}.', extra={'markup': True})

    def warning(self, class_name, message):
        self.logger.warning(f'[{class_name}] {message}.')

    def debug(self, class_name, message):
        message = str(pretty_repr(message))
        self.logger.debug(f'[bold yellow][{class_name}][/] Data: {message}.', extra={'markup': True})
