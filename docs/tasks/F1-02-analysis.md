## Analysis Report — F1-02

### Files read in full
- [src/ultron_jobs/core/exceptions/__init__.py](file:///c:/Users/YS%20TECH%20CENTER/Desktop/Job-CoPilot/src/ultron_jobs/core/exceptions/__init__.py) — Initial empty exception package module.
- [tests/unit/test_package_imports.py](file:///c:/Users/YS%20TECH%20CENTER/Desktop/Job-CoPilot/tests/unit/test_package_imports.py) — Top level import tests verifying package structure.

### Callers / dependents identified
- None. This is the foundational exception module. No existing classes import from it yet.

### Discrepancies found (docs vs. actual code)
- The exception package directory `src/ultron_jobs/core/exceptions/` exists but only contains a basic docstring in its `__init__.py`. We need to define the exception classes in submodules and export them.

### Risks / edge cases this task could affect
- **Ruff & Mypy validation**: Must satisfy Ruff rules and Mypy strict type checking configured for `ultron_jobs`.
- **JSON Serialization**: `to_dict()` must produce serializable dictionaries. We must make sure context initialization handles JSON primitives correctly.
- **Auto-derivation of `error_code`**: Must determine the code in `SCREAMING_SNAKE_CASE` based on the class name dynamically if not provided.

### Open questions (if any) — raised before implementation begins
- None. The hierarchy and design rules are fully specified.

### Proposed approach
1. Implement the base exception `UltronJobsError` in `src/ultron_jobs/core/exceptions/base.py` with dynamic `error_code` resolution, structured `context` dict initialization, custom `__str__`, and `to_dict()`.
2. Implement specific exception submodules: `config.py`, `infrastructure.py`, `application.py`, and `bootstrap.py` according to the hierarchy blueprint.
3. Expose them all via `src/ultron_jobs/core/exceptions/__init__.py` using explicit `__all__`.
4. Create the two unit test suites: `tests/unit/core/exceptions/test_base.py` (basic functionality) and `tests/unit/core/exceptions/test_hierarchy.py` (parentage/scaffolding tests).
