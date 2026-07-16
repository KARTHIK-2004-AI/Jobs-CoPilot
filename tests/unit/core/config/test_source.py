"""Unit tests for EnvConfigSource class."""

import pytest
from ultron_jobs.core.config.source import EnvConfigSource
from ultron_jobs.core.exceptions import MissingConfigError, InvalidConfigError


def test_get_str_basic():
    env = {"ULTRON_LOG_LEVEL": "DEBUG", "ULTRON_EMPTY": "", "ULTRON_WHITESPACE": "   "}
    source = EnvConfigSource(prefix="ULTRON_", env=env)

    # Basic retrieval
    assert source.get_str("LOG_LEVEL") == "DEBUG"
    # Default value fallback
    assert source.get_str("NON_EXISTENT", default="INFO") == "INFO"
    # None when optional and absent
    assert source.get_str("NON_EXISTENT") is None


def test_get_str_required_and_empty():
    env = {"ULTRON_LOG_LEVEL": "DEBUG", "ULTRON_EMPTY": "", "ULTRON_WHITESPACE": "   "}
    source = EnvConfigSource(prefix="ULTRON_", env=env)

    # Missing + required=True raises MissingConfigError
    with pytest.raises(MissingConfigError) as exc_info:
        source.get_str("NON_EXISTENT", required=True)
    assert "ULTRON_NON_EXISTENT" in str(exc_info.value)

    # Empty string + required=True raises MissingConfigError (counts as unset)
    with pytest.raises(MissingConfigError):
        source.get_str("EMPTY", required=True)

    # Whitespace-only string + required=True raises MissingConfigError (counts as unset)
    with pytest.raises(MissingConfigError):
        source.get_str("WHITESPACE", required=True)

    # Optional empty/whitespace returns default
    assert source.get_str("EMPTY", default="DEFAULT") == "DEFAULT"
    assert source.get_str("WHITESPACE", default="DEFAULT") == "DEFAULT"


def test_get_int_basic():
    env = {
        "ULTRON_PORT": "8080",
        "ULTRON_INVALID": "not-a-number",
        "ULTRON_EMPTY": "",
        "ULTRON_WHITESPACE": "  ",
    }
    source = EnvConfigSource(prefix="ULTRON_", env=env)

    # Basic retrieval
    assert source.get_int("PORT") == 8080
    # Default fallback
    assert source.get_int("NON_EXISTENT", default=5000) == 5000
    # None when optional and absent
    assert source.get_int("NON_EXISTENT") is None


def test_get_int_required_and_invalid():
    env = {
        "ULTRON_PORT": "8080",
        "ULTRON_INVALID": "not-a-number",
        "ULTRON_EMPTY": "",
    }
    source = EnvConfigSource(prefix="ULTRON_", env=env)

    # Missing + required=True raises MissingConfigError
    with pytest.raises(MissingConfigError):
        source.get_int("NON_EXISTENT", required=True)

    # Empty + required=True raises MissingConfigError
    with pytest.raises(MissingConfigError):
        source.get_int("EMPTY", required=True)

    # Invalid integer value raises InvalidConfigError
    with pytest.raises(InvalidConfigError) as exc_info:
        source.get_int("INVALID")
    assert "ULTRON_INVALID" in str(exc_info.value)
    assert "not-a-number" in str(exc_info.value)


def test_get_bool_basic():
    env = {
        "ULTRON_DEBUG_TRUE": "true",
        "ULTRON_DEBUG_1": "1",
        "ULTRON_DEBUG_YES": "yes",
        "ULTRON_DEBUG_ON": "ON",  # test case-insensitivity
        "ULTRON_DEBUG_FALSE": "false",
        "ULTRON_DEBUG_0": "0",
        "ULTRON_DEBUG_NO": "no",
        "ULTRON_DEBUG_OFF": "off",
        "ULTRON_INVALID": "maybe",
        "ULTRON_EMPTY": "",
    }
    source = EnvConfigSource(prefix="ULTRON_", env=env)

    # Truthy parses
    assert source.get_bool("DEBUG_TRUE") is True
    assert source.get_bool("DEBUG_1") is True
    assert source.get_bool("DEBUG_YES") is True
    assert source.get_bool("DEBUG_ON") is True

    # Falsy parses
    assert source.get_bool("DEBUG_FALSE") is False
    assert source.get_bool("DEBUG_0") is False
    assert source.get_bool("DEBUG_NO") is False
    assert source.get_bool("DEBUG_OFF") is False

    # Default fallback
    assert source.get_bool("NON_EXISTENT", default=True) is True
    assert source.get_bool("NON_EXISTENT") is None


def test_get_bool_required_and_invalid():
    env = {
        "ULTRON_INVALID": "maybe",
        "ULTRON_EMPTY": "",
    }
    source = EnvConfigSource(prefix="ULTRON_", env=env)

    # Missing + required=True raises MissingConfigError
    with pytest.raises(MissingConfigError):
        source.get_bool("NON_EXISTENT", required=True)

    # Empty + required=True raises MissingConfigError
    with pytest.raises(MissingConfigError):
        source.get_bool("EMPTY", required=True)

    # Invalid boolean value raises InvalidConfigError
    with pytest.raises(InvalidConfigError) as exc_info:
        source.get_bool("INVALID")
    assert "ULTRON_INVALID" in str(exc_info.value)
    assert "maybe" in str(exc_info.value)
