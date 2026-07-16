"""Core exception foundation for ULTRON Jobs.

Re-exports all foundational exception classes so they can be imported directly
from `ultron_jobs.core.exceptions`.
"""

from ultron_jobs.core.exceptions.application import (
    ApplicationError,
    UseCaseError,
    ValidationError,
)
from ultron_jobs.core.exceptions.base import UltronJobsError
from ultron_jobs.core.exceptions.bootstrap import (
    BootstrapError,
    DependencyInjectionError,
)
from ultron_jobs.core.exceptions.config import (
    ConfigurationError,
    InvalidConfigError,
    MissingConfigError,
)
from ultron_jobs.core.exceptions.infrastructure import (
    ExternalServiceError,
    InfrastructureError,
    ModelProviderError,
    PersistenceError,
)

__all__ = [
    "UltronJobsError",
    "ConfigurationError",
    "MissingConfigError",
    "InvalidConfigError",
    "InfrastructureError",
    "PersistenceError",
    "ExternalServiceError",
    "ModelProviderError",
    "ApplicationError",
    "ValidationError",
    "UseCaseError",
    "BootstrapError",
    "DependencyInjectionError",
]
