"""App initialization and dependency injection exception types."""

from ultron_jobs.core.exceptions.base import UltronJobsError


class BootstrapError(UltronJobsError):
    """Base exception for startup and boot sequence failures."""


class DependencyInjectionError(BootstrapError):
    """Exception raised when container wiring, service lookup, or DI registration fails."""
