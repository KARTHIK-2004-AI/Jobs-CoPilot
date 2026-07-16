"""Infrastructure and external service exception types."""

from ultron_jobs.core.exceptions.base import UltronJobsError


class InfrastructureError(UltronJobsError):
    """Base exception for all infrastructure layer errors."""


class PersistenceError(InfrastructureError):
    """Exception for database, file storage, or cache operations."""


class ExternalServiceError(InfrastructureError):
    """Exception for failures in external systems, services, or APIs."""


class ModelProviderError(ExternalServiceError):
    """Exception raised when an LLM provider (e.g. Gemini, OpenAI) fails or rate limits."""
