# Analysis Report — F1-04: Logging Setup (`core/logging/`)

This report details the architectural design and implementation plan for the idempotent, settings-driven logging configuration module under `ultron_jobs/core/logging/`.

---

## 1. Prerequisites Check
- `AppSettings` (from F1-03) has the following relevant fields:
  * `environment: str`
  * `log_level: str`
  * `debug: bool`
- `src/ultron_jobs/core/logging/__init__.py` is currently empty.
- Stblib `logging` will be used as the underlying logging library.

---

## 2. Design of `setup.py`

### `configure_logging(settings: AppSettings, *, stream: TextIO | None = None) -> None`
- **Level Validation**:
  - Convert `settings.log_level` to uppercase.
  - Resolve the numeric level value using `logging.getLevelNamesMapping().get(...)` (with `logging._nameToLevel.get(...)` as a fallback for older Python runtimes).
  - If the resolved level is `None`, raise `InvalidConfigError` (imported from `core.exceptions`).
- **Formatter configuration**:
  - Standard format: `"%(asctime)s [%(levelname)s] %(name)s: %(message)s"`
  - Debug format (when `settings.debug` is True): `"%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"`
- **Idempotency (Duplicate Handler Prevention)**:
  - Iterate through `logging.root.handlers` and remove any handlers containing a specific custom attribute tag (e.g. `_ultron_jobs_logger`).
  - Create a new `StreamHandler` targeting the provided `stream` (defaulting to `sys.stderr`).
  - Set the formatter on the new handler.
  - Mark the handler with the custom attribute: `handler._ultron_jobs_logger = True`.
  - Add the handler to `logging.root` and set root logging level using `logging.root.setLevel(level)`.

### `get_logger(name: str) -> logging.Logger`
- Returns `logging.getLogger(name)` directly.
- Avoids calling `configure_logging()` inside `get_logger()`, delegating that execution to the bootstrapping layer.

---

## 3. Design of `__init__.py`
Re-export the logging functions:
```python
from ultron_jobs.core.logging.setup import configure_logging, get_logger

__all__ = ["configure_logging", "get_logger"]
```

---

## 4. Verification Plan

### Automated Tests
We will implement:
- `tests/unit/core/logging/test_setup.py`:
  - Test level mapping and validation (raising `InvalidConfigError` on invalid levels).
  - Test idempotency (calling `configure_logging` multiple times leaves exactly one custom handler on `logging.root`).
  - Test formatter outputs under `debug=True` and `debug=False` using `io.StringIO()` to capture logs.
  - Test that the global logging configuration is correctly cleaned up (restoring previous handlers and level) in a test fixture teardown to prevent state leakage to other tests.

### Regression checks
- Run `pytest` on all tests (both legacy and core).
- Verify `applypilot status` works as expected.
