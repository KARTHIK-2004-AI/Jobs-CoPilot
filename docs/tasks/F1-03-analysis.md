# Analysis Report — F1-03: Configuration Management (`core/config/`)

This report summarizes the design analysis for establishing generic, typed configuration loading in `ultron_jobs/core/config/` per the task requirements and constraints.

---

## 1. Exceptions & Scaffolding Check
- The core exception signatures (`ConfigurationError`, `MissingConfigError`, `InvalidConfigError`) require:
  ```python
  def __init__(self, message: str, *, error_code: str | None = None, context: dict[str, object] | None = None) -> None
  ```
- `src/ultron_jobs/core/config/__init__.py` is currently an empty module placeholder.
- We will raise these exceptions directly when configuration variables are missing or invalid/malformed.

---

## 2. Design of `source.py` (`EnvConfigSource`)
We will create `src/ultron_jobs/core/config/source.py` with the class `EnvConfigSource`:
- Constructor signature:
  ```python
  def __init__(self, prefix: str = "ULTRON_", env: Mapping[str, str] | None = None) -> None:
      self._prefix = prefix
      self._env = env if env is not None else os.environ
  ```
- Implement `get_str(self, key: str, *, default: str | None = None, required: bool = False) -> str | None`:
  - Prepends `self._prefix` to `key` to look it up in `self._env`.
  - Checks if value is present and non-empty/non-whitespace.
  - If empty/whitespace:
    - If `required=True` -> raises `MissingConfigError`.
    - Otherwise, returns `default`.
  - Returns the non-empty string.
- Implement `get_int(self, key: str, *, default: int | None = None, required: bool = False) -> int | None`:
  - Retrieves raw string using `get_str`.
  - If string is `None`: returns `default`.
  - Otherwise, attempts to parse as integer. If parsing fails, raises `InvalidConfigError`.
- Implement `get_bool(self, key: str, *, default: bool | None = None, required: bool = False) -> bool | None`:
  - Retrieves raw string using `get_str`.
  - If string is `None`: returns `default`.
  - Converts string to lowercase and checks against:
    - Truthy: `"true"`, `"1"`, `"yes"`, `"on"` (or any others specified).
    - Falsy: `"false"`, `"0"`, `"no"`, `"off"`.
  - If not in either list, raises `InvalidConfigError`.

---

## 3. Design of `settings.py` (`AppSettings` & `load_settings`)
We will create `src/ultron_jobs/core/config/settings.py` containing:
- Class `AppSettings` (frozen dataclass):
  ```python
  @dataclass(frozen=True)
  class AppSettings:
      environment: str  # Must be "development", "staging", or "production"
      log_level: str    # Must be "DEBUG", "INFO", "WARNING", "ERROR", etc.
      debug: bool
  ```
- Function `load_settings(source: EnvConfigSource | None = None) -> AppSettings`:
  - If `source` is not provided, defaults to `EnvConfigSource()`.
  - Reads `environment` using `source.get_str("ENVIRONMENT", default="development")`.
  - Reads `log_level` using `source.get_str("LOG_LEVEL", default="INFO")`.
  - Reads `debug` using `source.get_bool("DEBUG", default=False)`.
  - Validates `environment` is in `("development", "staging", "production")`. If not, raises `InvalidConfigError`.
  - Validates `log_level` is in `("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")`. If not, raises `InvalidConfigError`.
  - Instantiates and returns `AppSettings`.

---

## 4. Design of `__init__.py`
Re-export classes:
```python
from ultron_jobs.core.config.source import EnvConfigSource
from ultron_jobs.core.config.settings import AppSettings, load_settings

__all__ = ["EnvConfigSource", "AppSettings", "load_settings"]
```

---

## 5. Verification Plan

### Automated Tests
We will implement:
- `tests/unit/core/config/test_source.py`: testing all types of retrievals, defaults, required handling, and edge cases.
- `tests/unit/core/config/test_settings.py`: testing default config loading, valid override configs, and validation errors.

### Regression checks
We will run existing tests and verify `applypilot status` to confirm everything is green and unmodified.
