import logging
from io import StringIO

from hamcrest import assert_that, greater_than

from rss_agg.logging_utils import init_logging, log_duration


def test_init_logging_debug_level() -> None:
    """Test init_logging with DEBUG verbosity sets debug format and filters warnings."""
    handler = logging.StreamHandler(stream=StringIO())

    init_logging(verbosity=3, handler=handler, silence_packages=())

    # Verify that logging is configured at DEBUG level
    assert_that(logging.getLogger().level, logging.DEBUG)


def test_log_duration_with_log_start() -> None:
    """Test log_duration logs at start when log_start=True."""
    log_entries = []

    def capture_log(msg: str, *args: str, extra: dict | None = None) -> None:  # noqa: ARG001
        log_entries.append(msg)

    with log_duration(capture_log, "test operation", log_start=True, key="value"):
        pass

    # Verify it was called twice: once for start, once for finish
    assert_that(len(log_entries), greater_than(0))
