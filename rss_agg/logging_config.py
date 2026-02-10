import logging
import sys
import warnings
from typing import TYPE_CHECKING

from pythonjsonlogger.json import JsonFormatter

if TYPE_CHECKING:
    from collections.abc import Sequence

LOG_LEVELS = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]


def init_logging(
    verbosity: int,
    handler: logging.Handler | None = None,
    silence_packages: Sequence[str] = (),
) -> None:
    """Initialize logging configuration with JSON formatting.

    Args:
        verbosity: Log level as an index into LOG_LEVELS (0=ERROR, 1=WARNING, 2=INFO, 3=DEBUG)
        handler: Optional handler to use. Defaults to StreamHandler(stdout)
        silence_packages: Package names to silence (set to WARNING level minimum)
    """
    handler = handler or logging.StreamHandler(stream=sys.stdout)
    level = LOG_LEVELS[min(verbosity, len(LOG_LEVELS) - 1)]
    msg_format = "%(message)s"
    if level <= logging.DEBUG:
        warnings.filterwarnings("ignore")
        msg_format = "%(asctime)s %(levelname)-8s %(name)s %(module)s.py:%(funcName)s():%(lineno)d %(message)s"
    handler.setFormatter(JsonFormatter(msg_format))
    logging.basicConfig(level=level, format=msg_format, handlers=[handler])

    for package in silence_packages:
        logging.getLogger(package).setLevel(max([level, logging.WARNING]))
