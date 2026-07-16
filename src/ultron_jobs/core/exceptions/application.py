"""Application layer and business logic exception types."""

from ultron_jobs.core.exceptions.base import UltronJobsError


class ApplicationError(UltronJobsError):
    """Base exception for all application layer errors."""


class ValidationError(ApplicationError):
    """Exception raised when user input or request payload fails validation checks."""


class UseCaseError(ApplicationError):
    """Exception raised when a business rule or use case logic is violated."""
