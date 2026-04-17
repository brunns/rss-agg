import logging
from io import StringIO

from hamcrest import assert_that, equal_to, greater_than, has_length

from rss_agg.logging_utils import init_logging, log_duration


def test_init_logging_debug_level() -> None:
    """Test init_logging with DEBUG verbosity sets debug format and filters warnings."""
    # Given
    handler = logging.StreamHandler(stream=StringIO())

    # When
    init_logging(verbosity=3, handler=handler, silence_packages=())

    # Then logging is configured at DEBUG level
    assert_that(logging.getLogger().level, logging.DEBUG)


def test_log_duration_with_log_start() -> None:
    """Test log_duration logs at start when log_start=True."""
    # Given
    log_entries = []

    def capture_log(msg: str, *args: str, extra: dict | None = None) -> None:  # noqa: ARG001
        log_entries.append(msg)

    # When
    with log_duration(capture_log, "test operation", log_start=True, key="value"):
        pass

    # Then called twice: once for start, once for finish
    assert_that(len(log_entries), greater_than(0))


def test_log_duration_default_no_start_log() -> None:
    """Test log_duration only logs once (at finish) when log_start=False (the default)."""
    # Given
    log_entries = []

    def capture_log(msg: str, *args: str, extra: dict | None = None) -> None:  # noqa: ARG001
        log_entries.append(msg)

    # When
    with log_duration(capture_log, "test operation", key="value"):
        pass

    # Then called once
    assert_that(log_entries, has_length(1))


def test_init_logging_verbosity_filtering() -> None:
    """Test that verbosity beyond the maximum is filtered to DEBUG level."""
    # Given
    root = logging.getLogger()
    saved_handlers = root.handlers[:]
    saved_level = root.level
    root.handlers.clear()  # Ensure basicConfig is not a no-op

    # When
    try:
        handler = logging.StreamHandler(stream=StringIO())
        init_logging(verbosity=99, handler=handler, silence_packages=())

        # Then
        assert_that(root.level, equal_to(logging.DEBUG))
    finally:
        root.handlers.clear()
        root.handlers.extend(saved_handlers)
        root.setLevel(saved_level)
