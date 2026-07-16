# Task F1-02: Exception Hierarchy (`core/exceptions/`)

**Sprint:** 1 — Engineering Foundation
**Status:** Ready for builder
**Depends on:** F1-01 (repo scaffolding + CI) — approved
**Architectural concern (single):** Establish the project-wide exception hierarchy under `core/exceptions/`. Nothing else.

---

## Step 0 — Mandatory Analysis (do this before writing any code)

Follow `docs/BUILDER_ANALYSIS_PROTOCOL.md` in full. Concretely, for this task:

1. Read the current repo state as left by F1-01 in full — don't assume the
   scaffolding matches what F1-01's task file described; confirm what's
   actually there (`src/ultron_jobs/core/` layout, `pyproject.toml`, CI config,
   test config/fixtures).
2. Confirm `src/ultron_jobs/core/exceptions/` doesn't already exist or partially
   exist from F1-01 — if it does, read it fully before deciding whether to
   extend or flag a conflict.
3. Read `src/applypilot/` only to the extent needed to confirm it is *not*
   going to be touched — do not read it looking for reasons to "improve" it,
   that's out of scope by definition (see Forbidden Changes).
4. Produce the Analysis Report (per the protocol) as
   `docs/tasks/F1-02-analysis.md` and stop there for review before starting
   implementation.

---

## Objective

Create a small, structured exception hierarchy in `src/ultron_jobs/core/exceptions/` that every later layer (infrastructure, application, interface) will subclass or raise. This task produces **only** the exception types and their tests — no call sites, no wiring into `applypilot`, no domain logic.

## Background

Per ADR-001, Sprint 1 is scoped to engineering foundation only (config, logging, DI/bootstrap, exceptions, testing infra, CI), with **zero job-domain logic**. F1-01 established the repo skeleton and CI. This task is the next Foundation item per the revised roadmap. Domain-specific exceptions (e.g., `JobNotFoundError`, `ScoringFailedError`) are explicitly **out of scope** — those belong to Sprint 3 (`domain/exceptions.py`) once domain models exist. This task builds only the generic, reusable base layer that domain/application/infrastructure exceptions will later inherit from.

## Business Context

Founder is building ULTRON Jobs as a standalone product first, with disciplined production-grade engineering practice (not moving fast and skipping structure). A consistent exception hierarchy is foundational: it lets later layers (LLM provider errors, persistence errors, config errors) all be caught, logged, and reported uniformly by the CLI/MCP interface layers built in later sprints — without those interfaces needing to know about every concrete error type.

## Architecture Context

Per the target directory structure (ADR-001):
```
src/ultron_jobs/
├── core/{config,logging,exceptions,bootstrap,constants}/
```
Rule reminder: `core/` has no dependency on `domain`, `application`, or `infrastructure`. It is the lowest layer — everything else may import from it, it imports nothing project-internal. This task must respect that: exceptions defined here must not import or reference anything outside `core/` and the Python standard library.

This task does **not** touch `src/applypilot/` (the existing working pipeline) in any way — that code has its own error handling and is untouched until its own migration sprint (Sprints 6+).

## Files

Create:
- `src/ultron_jobs/core/exceptions/__init__.py`
- `src/ultron_jobs/core/exceptions/base.py`
- `src/ultron_jobs/core/exceptions/config.py`
- `src/ultron_jobs/core/exceptions/infrastructure.py`
- `src/ultron_jobs/core/exceptions/application.py`
- `src/ultron_jobs/core/exceptions/bootstrap.py`
- `tests/unit/core/exceptions/test_base.py`
- `tests/unit/core/exceptions/test_hierarchy.py`

Do not create, modify, or delete any file outside this list and their `__init__.py`/`conftest.py` scaffolding needed purely to make the test package importable (if `tests/unit/core/` or `tests/unit/core/exceptions/` don't yet have `__init__.py`, add empty ones — nothing else).

## Interfaces

### `base.py`
```python
class UltronJobsError(Exception):
    """Base exception for all ULTRON Jobs errors.

    Attributes:
        message: Human-readable description.
        error_code: Short stable machine-readable code, e.g. "CONFIG_MISSING".
                    Defaults to the class name in SCREAMING_SNAKE_CASE if not given.
        context: Optional dict of structured debugging context (never put
                 secrets/API keys in here — see Constraints).
    """
    def __init__(self, message: str, *, error_code: str | None = None,
                 context: dict[str, object] | None = None) -> None: ...

    def __str__(self) -> str: ...       # "[ERROR_CODE] message"
    def to_dict(self) -> dict: ...      # {"error_code", "message", "context"} for logging/JSON
```

### `config.py`
```python
class ConfigurationError(UltronJobsError): ...
class MissingConfigError(ConfigurationError): ...
class InvalidConfigError(ConfigurationError): ...
```

### `infrastructure.py`
```python
class InfrastructureError(UltronJobsError): ...
class PersistenceError(InfrastructureError): ...
class ExternalServiceError(InfrastructureError): ...
class ModelProviderError(ExternalServiceError): ...   # future home for Gemini/LLM errors
```

### `application.py`
```python
class ApplicationError(UltronJobsError): ...
class ValidationError(ApplicationError): ...
class UseCaseError(ApplicationError): ...
```

### `bootstrap.py`
```python
class BootstrapError(UltronJobsError): ...
class DependencyInjectionError(BootstrapError): ...
```

### `__init__.py`
Re-export every public class above so callers can do `from ultron_jobs.core.exceptions import ConfigurationError` without knowing the submodule. Define `__all__` explicitly (no wildcard star-exports).

## Constraints

- Every exception class must ultimately subclass `UltronJobsError`. No bare `Exception` subclasses anywhere in this tree.
- No exception's `__init__` may accept or store raw secrets (API keys, tokens, passwords). If a caller passes something secret-shaped into `context`, that is the caller's bug to avoid — this task does not need to implement redaction, just must not encourage it in docstrings/examples.
- No print statements, no logging calls, no I/O inside `core/exceptions/`. These classes are pure data — logging them is the caller's responsibility (future `core/logging` work).
- `error_code` auto-derivation (when not explicitly passed) must be deterministic and based only on `type(self).__name__` — no reflection tricks beyond that, no metaclasses.
- Type hints required on all public methods. Must pass whatever linter/type-checker config F1-01 established in CI (run it locally before calling this done).
- Do not add third-party dependencies. Standard library only.
- Do not create `domain/exceptions.py` or any `application/`, `infrastructure/`, or `interface/` files — those layers don't exist yet and are out of scope for this task and this sprint.

## Acceptance Criteria

1. All six hierarchy files exist with the exact classes listed above (names and parent classes must match — later tasks will `except InfrastructureError` etc. and depend on this shape).
2. `UltronJobsError.__str__()` returns `"[ERROR_CODE] message"`.
3. `UltronJobsError.to_dict()` returns a dict with exactly the keys `error_code`, `message`, `context` (context defaults to `{}`, never `None`, if not supplied).
4. Every leaf class in the hierarchy is a subclass (direct or transitive) of `UltronJobsError`, verified by a test that walks `UltronJobsError.__subclasses__()` recursively.
5. `from ultron_jobs.core.exceptions import <AnyClassAbove>` works for every class listed in Interfaces.
6. `core/exceptions/` has zero imports from `domain`, `application`, `infrastructure`, or `interface` (verified by a simple grep/AST-based test, not just manual review).
7. CI (from F1-01) passes green on the branch.
8. Regression gate passes: `applypilot status` and `applypilot run discover enrich score` behave identically pre/post change (this task shouldn't be able to affect them at all, since `src/applypilot/` is untouched — but the gate still runs to catch accidental scope creep).

## Edge Cases

- `UltronJobsError("msg")` with no `error_code` and no `context` — must not raise, must produce sane defaults (`error_code` derived from class name, `context == {}`).
- Passing `context={}` explicitly vs. omitting it — both must behave identically.
- Subclassing one of these exceptions from outside `core/` (e.g., a future `ModelProviderTimeoutError(ModelProviderError)` defined in `infrastructure/llm/`) must work without needing changes to `core/exceptions/` — confirm this isn't accidentally prevented (e.g., no `__init_subclass__` restrictions, no `Final` classes).
- `to_dict()` must produce JSON-serializable output for a `context` dict containing nested dicts/lists/primitives (don't need to handle arbitrary objects — just don't crash on the common case).

## Testing Requirements

- Unit tests only (no integration tests needed — nothing external is touched).
- `test_base.py`: covers `UltronJobsError` construction, defaults, `__str__`, `to_dict()`, and the "subclassing from outside the module works" edge case.
- `test_hierarchy.py`: covers the full class list from Interfaces exists, has correct parentage, and the "everything traces back to `UltronJobsError`" + "no cross-layer imports" checks from Acceptance Criteria 4 and 6.
- Target ≥95% line coverage on the six new files (this is a small, pure-data module — there's no excuse for less).
- Must run and pass under whatever `pytest` config/CI job F1-01 set up, with no changes to CI config itself.

## Forbidden Changes

- **Do not modify anything under `src/applypilot/`.** This is the existing working pipeline; it is off-limits until its migration sprint.
- Do not modify `.github/workflows/` or any CI configuration — if F1-01's CI doesn't pick up the new test files automatically, that's a bug to flag, not a reason to edit CI config in this task.
- Do not create `domain/`, `application/`, or `interface/` files or directories, even empty placeholders. Only `core/exceptions/` and its tests.
- Do not touch `core/config/`, `core/logging/`, `core/bootstrap/`, or `core/constants/` — those are separate Foundation tasks, not this one.
- Do not add or modify `pyproject.toml` / `requirements*.txt` — no new dependencies are needed for this task.
- Do not rename, move, or restructure anything from F1-01's approved scaffolding.

## Definition of Done

- [ ] `docs/tasks/F1-02-analysis.md` (Step 0 output) exists and was reviewed
      before implementation began.
- [ ] All 6 source files + 2 test files created exactly as scoped.
- [ ] All Acceptance Criteria pass.
- [ ] All Edge Cases have corresponding tests.
- [ ] ≥95% coverage on the new files.
- [ ] CI green.
- [ ] Regression gate (`applypilot status`, `applypilot run discover enrich score`) confirmed identical pre/post.
- [ ] No Forbidden Changes violated — builder confirms in PR description with an explicit `git diff --stat` showing only the files listed above (plus any strictly necessary empty `__init__.py` for test package discovery).
- [ ] PR opened against `main` (or the current integration branch) referencing this task file, ready for architect review.
