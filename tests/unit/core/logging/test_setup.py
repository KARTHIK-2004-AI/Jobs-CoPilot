"""Unit tests for logging configuration setup."""

import io
import logging
import pytest
from ultron_jobs.core.config.settings import AppSettings
from ultron_jobs.core.logging.setup import configure_logging, get_logger
from ultron_jobs.core.exceptions import InvalidConfigError


@pytest.fixture
def restore_logging_state():
    """Fixture to backup and restore logging handlers and level after test run."""
    # Backup
    orig_handlers = list(logging.root.handlers)
    orig_level = logging.root.level

    yield

    # Restore
    logging.root.handlers.clear()
    for h in orig_handlers:
        logging.root.addHandler(h)
    logging.root.setLevel(orig_level)


def test_configure_logging_levels(restore_logging_state):
    # Test setting valid log level
    settings = AppSettings(environment="development", log_level="WARNING", debug=False)
    configure_logging(settings)
    assert logging.root.level == logging.WARNING

    # Test setting invalid log level raises InvalidConfigError
    invalid_settings = AppSettings(environment="development", log_level="INVALID_LEVEL_NAME", debug=False)
    with pytest.raises(InvalidConfigError):
        configure_logging(invalid_settings)


def test_configure_logging_idempotency(restore_logging_state):
    settings = AppSettings(environment="development", log_level="INFO", debug=False)

    # First call
    configure_logging(settings)
    ultron_handlers_first = [h for h in logging.root.handlers if getattr(h, "_ultron_jobs_logger", False)]
    assert len(ultron_handlers_first) == 1

    # Second call
    configure_logging(settings)
    ultron_handlers_second = [h for h in logging.root.handlers if getattr(h, "_ultron_jobs_logger", False)]
    assert len(ultron_handlers_second) == 1  # Should not duplicate or stack


def test_configure_logging_formatting(restore_logging_state):
    # Test debug=False formatting
    settings_no_debug = AppSettings(environment="development", log_level="INFO", debug=False)
    stream_no_debug = io.StringIO()
    configure_logging(settings_no_debug, stream=stream_no_debug)

    logger = get_logger("test_no_debug")
    logger.info("this is a test log message")

    output_no_debug = stream_no_debug.getvalue()
    assert "[INFO] test_no_debug: this is a test log message" in output_no_debug
    assert "test_setup.py" not in output_no_debug  # should not have filename/line number

    # Test debug=True formatting
    settings_debug = AppSettings(environment="development", log_level="INFO", debug=True)
    stream_debug = io.StringIO()
    configure_logging(settings_debug, stream=stream_debug)

    logger = get_logger("test_debug")
    logger.info("another debug level log")

    output_debug = stream_debug.getvalue()
    assert "[INFO] test_debug" in output_debug
    assert "another debug level log" in output_debug
    assert "test_setup.py" in output_debug  # should have filename
    assert ":" in output_debug  # line number separator


def test_get_logger_caching():
    # Calling get_logger twice with the same name returns consistent instance
    logger1 = get_logger("my_unique_logger")
    logger2 = get_logger("my_unique_logger")
    assert logger1 is logger2
