"""Unit tests for load_settings and AppSettings."""

import pytest
from ultron_jobs.core.config.source import EnvConfigSource
from ultron_jobs.core.config.settings import load_settings, AppSettings
from ultron_jobs.core.exceptions import InvalidConfigError


def test_load_settings_defaults():
    # Empty environment configuration
    source = EnvConfigSource(prefix="ULTRON_", env={})
    settings = load_settings(source)

    assert isinstance(settings, AppSettings)
    assert settings.environment == "development"
    assert settings.log_level == "INFO"
    assert settings.debug is False


def test_load_settings_valid_overrides():
    env = {
        "ULTRON_ENVIRONMENT": "production",
        "ULTRON_LOG_LEVEL": "WARNING",
        "ULTRON_DEBUG": "true",
    }
    source = EnvConfigSource(prefix="ULTRON_", env=env)
    settings = load_settings(source)

    assert settings.environment == "production"
    assert settings.log_level == "WARNING"
    assert settings.debug is True


def test_load_settings_invalid_environment():
    env = {"ULTRON_ENVIRONMENT": "invalid-env"}
    source = EnvConfigSource(prefix="ULTRON_", env=env)

    with pytest.raises(InvalidConfigError) as exc_info:
        load_settings(source)
    assert "Invalid environment 'invalid-env'" in str(exc_info.value)
    assert "ULTRON_ENVIRONMENT" in exc_info.value.context["key"]


def test_load_settings_invalid_log_level():
    env = {"ULTRON_LOG_LEVEL": "INVALID_LEVEL"}
    source = EnvConfigSource(prefix="ULTRON_", env=env)

    with pytest.raises(InvalidConfigError) as exc_info:
        load_settings(source)
    assert "Invalid log level 'INVALID_LEVEL'" in str(exc_info.value)
    assert "ULTRON_LOG_LEVEL" in exc_info.value.context["key"]
