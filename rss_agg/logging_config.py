import logging
import sys
import time
import warnings
from contextlib import contextmanager
from typing import TYPE_CHECKING

from pythonjsonlogger.json import JsonFormatter

if TYPE_CHECKING:
    from collections.abc import Generator, Sequence

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


@contextmanager
def log_duration(logger: logging.Logger, message: str, **extra: str) -> Generator[None]:
    """Context manager to log the duration of a block of code.

    Args:
        logger: Logger instance to use
        message: Log message to output
        **extra: Additional fields to include in the log entry

    Example:
        with log_duration(logger, "request", path="/api/data"):
            # Do work here
            pass
    """

    start_time = time.perf_counter()
    logger.info("%s started", message, extra={**extra})
    try:
        yield
    finally:
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info("%s finished", message, extra={**extra, "duration_ms": f"{duration_ms:.2f}"})
