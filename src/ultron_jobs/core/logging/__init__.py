"""Core logging foundation for ULTRON Jobs.

Re-exports logging setup and retrieval primitives.
"""

from ultron_jobs.core.logging.setup import configure_logging, get_logger

__all__ = ["configure_logging", "get_logger"]
