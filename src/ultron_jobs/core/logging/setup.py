"""Logging configuration and retrieval utilities for ULTRON Jobs."""

import sys
import logging
from typing import TextIO
from ultron_jobs.core.config.settings import AppSettings
from ultron_jobs.core.exceptions import InvalidConfigError


def configure_logging(settings: AppSettings, *, stream: TextIO | None = None) -> None:
    """Configure the root logger from AppSettings.

    - Sets root logger level from settings.log_level (re-validated defensively).
    - Installs exactly one StreamHandler (defaults to sys.stderr if `stream`
      not given).
    - IDEMPOTENT: calling this more than once must not stack duplicate
      handlers — remove any handlers this function previously added before
      adding a new one.
    - Format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    - If settings.debug is True, format additionally includes
      "%(filename)s:%(lineno)d".
    """
    level_name = settings.log_level.upper()
    try:
        # Python 3.11+ preferred
        levels = logging.getLevelNamesMapping()
        level = levels.get(level_name)
    except AttributeError:
        # Fallback for older Python versions
        level = logging._nameToLevel.get(level_name)

    if level is None:
        raise InvalidConfigError(
            f"Log level '{settings.log_level}' is not a valid logging level name.",
            context={"log_level": settings.log_level},
        )

    # Determine formatter based on debug flag
    if settings.debug:
        fmt = "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"
    else:
        fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    # Idempotently clean up previously added handlers by this module
    for h in list(logging.root.handlers):
        if getattr(h, "_ultron_jobs_logger", False):
            logging.root.removeHandler(h)

    # Set up stream handler
    target_stream = stream if stream is not None else sys.stderr
    handler = logging.StreamHandler(target_stream)
    handler.setFormatter(logging.Formatter(fmt))
    
    # Tag handler for idempotency
    setattr(handler, "_ultron_jobs_logger", True)

    logging.root.addHandler(handler)
    logging.root.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """Thin wrapper around logging.getLogger(name). Exists so call sites
    import from ultron_jobs.core.logging instead of stdlib logging directly —
    a single seam if structured/JSON logging is added in a later sprint.
    Does not call configure_logging itself; configuration is the caller's
    (eventually core/bootstrap's) responsibility, done once at startup.
    """
    return logging.getLogger(name)
