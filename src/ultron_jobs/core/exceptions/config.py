"""Configuration exception types."""

from ultron_jobs.core.exceptions.base import UltronJobsError


class ConfigurationError(UltronJobsError):
    """Base exception for all configuration errors."""


class MissingConfigError(ConfigurationError):
    """Exception raised when a required configuration key or file is missing."""


class InvalidConfigError(ConfigurationError):
    """Exception raised when a configuration value is invalid or malformed."""
