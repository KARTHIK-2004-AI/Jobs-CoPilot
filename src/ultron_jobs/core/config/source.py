"""Configuration source logic for ULTRON Jobs."""

import os
from typing import Mapping
from ultron_jobs.core.exceptions import MissingConfigError, InvalidConfigError


class EnvConfigSource:
    """Reads typed configuration values from environment variables.

    Args:
        prefix: Prepended to every key looked up, e.g. "ULTRON_" so
                get_str("LOG_LEVEL") reads the ULTRON_LOG_LEVEL env var.
        env: Optional explicit mapping to read from instead of os.environ
             (primarily for testing — production code should omit this and
             let it default to os.environ).
    """

    def __init__(
        self,
        prefix: str = "ULTRON_",
        env: Mapping[str, str] | None = None,
    ) -> None:
        self._prefix = prefix
        self._env = env if env is not None else os.environ

    def get_str(
        self,
        key: str,
        *,
        default: str | None = None,
        required: bool = False,
    ) -> str | None:
        """Retrieve a string configuration value.

        Raises:
            MissingConfigError: If required=True and the value is missing or empty.
        """
        full_key = f"{self._prefix}{key}"
        raw_val = self._env.get(full_key)

        if raw_val is not None:
            stripped = raw_val.strip()
            if stripped == "":
                raw_val = None
            else:
                raw_val = stripped

        if raw_val is None:
            if required:
                raise MissingConfigError(
                    f"Required configuration key '{full_key}' is missing.",
                    context={"key": full_key},
                )
            return default

        return raw_val

    def get_int(
        self,
        key: str,
        *,
        default: int | None = None,
        required: bool = False,
    ) -> int | None:
        """Retrieve an integer configuration value.

        Raises:
            MissingConfigError: If required=True and the value is missing or empty.
            InvalidConfigError: If the value is present but not a valid integer.
        """
        raw_val = self.get_str(key, required=required)
        if raw_val is None:
            return default

        try:
            return int(raw_val)
        except ValueError as e:
            full_key = f"{self._prefix}{key}"
            raise InvalidConfigError(
                f"Configuration key '{full_key}' has invalid integer value '{raw_val}'.",
                context={"key": full_key, "value": raw_val},
            ) from e

    def get_bool(
        self,
        key: str,
        *,
        default: bool | None = None,
        required: bool = False,
    ) -> bool | None:
        """Retrieve a boolean configuration value.

        Accepts case-insensitive: true/false/1/0/yes/no/on/off.

        Raises:
            MissingConfigError: If required=True and the value is missing or empty.
            InvalidConfigError: If the value is present but not a valid boolean string.
        """
        raw_val = self.get_str(key, required=required)
        if raw_val is None:
            return default

        lower_val = raw_val.lower()
        if lower_val in ("true", "1", "yes", "on"):
            return True
        if lower_val in ("false", "0", "no", "off"):
            return False

        full_key = f"{self._prefix}{key}"
        raise InvalidConfigError(
            f"Configuration key '{full_key}' has invalid boolean value '{raw_val}'.",
            context={"key": full_key, "value": raw_val},
        )
