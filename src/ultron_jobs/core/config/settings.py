"""Application settings definition for ULTRON Jobs."""

from dataclasses import dataclass
from ultron_jobs.core.exceptions import InvalidConfigError
from ultron_jobs.core.config.source import EnvConfigSource


@dataclass(frozen=True)
class AppSettings:
    """Foundation-level application settings. Generic only — no job-domain
    fields belong here. Later sprints add their own settings objects
    (e.g. LLMProviderSettings) that compose alongside this, not inside it.
    """
    environment: str
    log_level: str
    debug: bool


def load_settings(source: EnvConfigSource | None = None) -> AppSettings:
    """Build AppSettings from an EnvConfigSource (defaults to a fresh one
    reading os.environ). Validates environment is one of the three allowed
    values and log_level is a valid logging level name; raises
    InvalidConfigError otherwise. Applies sane defaults:
    environment="development", log_level="INFO", debug=False — none of the
    three env vars are required to be set.
    """
    if source is None:
        source = EnvConfigSource()

    env_val = source.get_str("ENVIRONMENT", default="development")
    log_level_val = source.get_str("LOG_LEVEL", default="INFO")
    debug_val = source.get_bool("DEBUG", default=False)

    valid_environments = ("development", "staging", "production")
    if env_val not in valid_environments:
        raise InvalidConfigError(
            f"Invalid environment '{env_val}'. Must be one of: {', '.join(valid_environments)}",
            context={"key": f"{source._prefix}ENVIRONMENT", "value": env_val},
        )

    valid_log_levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    if log_level_val not in valid_log_levels:
        raise InvalidConfigError(
            f"Invalid log level '{log_level_val}'. Must be one of: {', '.join(valid_log_levels)}",
            context={"key": f"{source._prefix}LOG_LEVEL", "value": log_level_val},
        )

    return AppSettings(
        environment=env_val,
        log_level=log_level_val,
        debug=bool(debug_val),
    )
