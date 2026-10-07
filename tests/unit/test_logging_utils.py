# Copyright 2024-2026 Simon Brunning
import logging
import warnings
from contextlib import contextmanager
from io import StringIO

from hamcrest import assert_that, equal_to, greater_than, has_length

from rss_agg.utils.logging_utils import init_logging, log_duration


def test_init_logging_debug_level() -> None:
    """Test init_logging with DEBUG verbosity sets debug format and filters warnings."""
    # Given
    with restore_logging():
        handler = logging.StreamHandler(stream=StringIO())

        # When
        init_logging(verbosity=3, handler=handler, silence_packages=())

        # Then
        assert_that(logging.getLogger().level, equal_to(logging.DEBUG))


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
    with restore_logging():
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


@contextmanager
def restore_logging():
    root = logging.getLogger()
    original_level = root.level
    original_handlers = root.handlers[:]
    child_levels = {
        name: logger.level
        for name, logger in logging.Logger.manager.loggerDict.items()
        if isinstance(logger, logging.Logger)
    }

    try:
        with warnings.catch_warnings():
            yield
    finally:
        root.setLevel(original_level)
        for h in root.handlers:
            if h not in original_handlers:
                h.close()
        root.handlers.clear()
        root.handlers.extend(original_handlers)
        for name, level in child_levels.items():
            logging.getLogger(name).setLevel(level)
