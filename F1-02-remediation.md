# Task F1-02-REMEDIATION: Fix Scope Violations on `feat/f1-01-repo-scaffolding`

**Sprint:** 1 — Engineering Foundation
**Status:** Ready for builder
**Applies to branch:** `feat/f1-01-repo-scaffolding`
**Depends on:** F1-02 (exception hierarchy) — code approved in principle, branch rejected due to scope violations
**Architectural concern (single):** Restore the branch to contain ONLY the F1-02 exception-hierarchy work. Nothing else.

---

## Why this task exists

Architect review of the branch found the exception hierarchy itself (`core/exceptions/`)
correctly implemented and close to mergeable. However, the same branch also contains
a second, undisclosed set of changes that violate F1-02's Forbidden Changes section —
the same category of violation (`src/applypilot/` modified) that was already caught
and fixed once during the F1-01 review. This is not a new task to design something —
it is a cleanup task to remove what should never have been added, and relocate what
was added in the wrong place. **Do not use this task as an opportunity to redesign
anything.** Revert means revert.

## Step 0 — Mandatory Analysis (per `docs/BUILDER_ANALYSIS_PROTOCOL.md`)

Before making any changes:
1. Run `git diff main...feat/f1-01-repo-scaffolding --stat` and confirm it matches
   the file list below. If it doesn't match, stop and report the discrepancy —
   do not guess at what changed.
2. Read the full diff for each file in **Section A (revert)** below and confirm
   you understand exactly what will be undone.
3. Do not proceed to Step 1 until you can state, in the PR description, that
   the diff after this task will contain only `core/exceptions/`,
   `tests/unit/core/exceptions/`, `docs/tasks/F1-02-analysis.md`, and the doc
   relocations in Section B.

---

## Section A — REVERT (undo these files back to `main`, no trace of the change)

These files must end up **byte-identical to their `main` branch version**. Do not
selectively keep "the good parts" of the change — the entire diff on each file
goes away. The functionality being removed (API key rotation, `--limit` flag,
`load_dotenv(override=True)`) is legitimate and wanted, but it belongs in its
own reviewed task, not silently bundled here.

| File | Action |
|---|---|
| `src/applypilot/cli.py` | Revert to `main` — removes the `--limit` flag |
| `src/applypilot/config.py` | Revert to `main` — removes `override=True` on `load_dotenv()` |
| `src/applypilot/llm.py` | Revert to `main` — removes key-rotation logic entirely |
| `src/applypilot/pipeline.py` | Revert to `main` — removes `limit` threading through all stage runners |
| `.github/workflows/ci.yml` | Revert to `main` — removes the added lint/typecheck/unit jobs |
| `pyproject.toml` | Revert to `main` — removes `mypy` dependency, ruff line-length change, `[tool.mypy]` block |
| `README.md` | Revert to `main` — this also fixes the corrupted sentence under "Tailor" (currently reads "emphasizes ~/.applypilot/.envrelevant skills" — a stray path string got pasted mid-sentence) |

Suggested mechanics (adjust for whatever the actual working setup is):
```bash
git checkout main -- src/applypilot/cli.py src/applypilot/config.py \
  src/applypilot/llm.py src/applypilot/pipeline.py \
  .github/workflows/ci.yml pyproject.toml README.md
```
Confirm afterward with `git diff main -- <each file above>` producing empty output.

**Exception:** the one *legitimate* `.gitignore` change from F1-01 (`.venv/` entry)
must be preserved — do not revert `.gitignore` all the way to pre-F1-01. Only
remove the additions from this round (test-artifact ignores, mypy/tox ignores,
docs build ignores, `*.md~`/`*.md.bak` patterns) that came in alongside the
unauthorized work. If unsure which lines are which, show the current `.gitignore`
diff against `main` in the PR description before editing, so it can be checked.

## Section B — DELETE (stray artifacts, not part of any task's file list)

```bash
git rm diff_summary.txt
git rm test_configured_llm.py test_gemini.py test_key_rotation.py
```
These were debugging scripts for the key-rotation work being reverted in Section A.
If any of them contain useful diagnostic logic for the `fit_score = 0` investigation,
do not lose that work — but it does not belong committed to this branch. Paste the
content into the PR description or a scratch note for the architect to review
separately; don't silently discard if there's something worth keeping.

Also remove `tests/unit/test_package_imports.py` **only if** it is not part of
F1-01's approved scope — check the F1-01 approval notes first. If it was part of
F1-01's approved deliverable, leave it. If it was added in this round alongside
the other unauthorized work, remove it.

## Section C — RELOCATE (move, don't delete — wrong location only)

| Current path | Correct path |
|---|---|
| `BUILDER_ANALYSIS_PROTOCOL.md` (repo root) | `docs/BUILDER_ANALYSIS_PROTOCOL.md` |
| `CLAUDE_MASTER_DIRECTIVE.md` (repo root) | `docs/CLAUDE_MASTER_DIRECTIVE.md` |
| `F1-02-exception-hierarchy.md` (repo root) | `docs/tasks/F1-02-exception-hierarchy.md` |

```bash
mkdir -p docs
git mv BUILDER_ANALYSIS_PROTOCOL.md docs/BUILDER_ANALYSIS_PROTOCOL.md
git mv CLAUDE_MASTER_DIRECTIVE.md docs/CLAUDE_MASTER_DIRECTIVE.md
git mv F1-02-exception-hierarchy.md docs/tasks/F1-02-exception-hierarchy.md
```
`docs/tasks/F1-02-analysis.md` is already in the right place — leave it.

## Section D — KEEP AS-IS (already correct, do not touch)

- `src/ultron_jobs/core/exceptions/__init__.py`
- `src/ultron_jobs/core/exceptions/base.py`
- `src/ultron_jobs/core/exceptions/config.py`
- `src/ultron_jobs/core/exceptions/infrastructure.py`
- `src/ultron_jobs/core/exceptions/application.py`
- `src/ultron_jobs/core/exceptions/bootstrap.py`
- `tests/unit/core/exceptions/test_base.py`
- `tests/unit/core/exceptions/test_hierarchy.py`
- `tests/unit/core/__init__.py`, `tests/unit/core/exceptions/__init__.py`
- `docs/tasks/F1-02-analysis.md`

This is the actual F1-02 deliverable and was reviewed as correct. No edits needed
here as part of this remediation — if you notice something wrong while reviewing
it, flag it in the PR description rather than fixing it silently; that's a
separate decision from "did the remediation succeed."

---

## Constraints

- This task only reverts, deletes, and relocates. It does not add new logic,
  does not refactor the exception hierarchy, does not "improve" anything.
- Do not re-derive or re-justify the key-rotation / `--limit` work — that gets
  its own task (tentatively F1-03 or a dedicated bugfix task) after this branch
  is clean. Don't pre-empt that review by leaving partial pieces of it behind.
- If any revert conflicts with the exception-hierarchy files (e.g., import
  ordering changes that touched a shared file), stop and report the conflict —
  do not resolve it by picking a side unilaterally.

## Acceptance Criteria

1. `git diff main...feat/f1-01-repo-scaffolding -- src/applypilot/` is empty.
2. `git diff main...feat/f1-01-repo-scaffolding -- .github/workflows/ci.yml pyproject.toml README.md` is empty.
3. `.gitignore` diff against `main` contains only the F1-01-approved `.venv/` addition — nothing from this round.
4. `diff_summary.txt`, `test_configured_llm.py`, `test_gemini.py`, `test_key_rotation.py` no longer exist on the branch.
5. `BUILDER_ANALYSIS_PROTOCOL.md`, `CLAUDE_MASTER_DIRECTIVE.md`, `F1-02-exception-hierarchy.md` exist under `docs/` / `docs/tasks/`, not at repo root.
6. `src/ultron_jobs/core/exceptions/` and its tests are unchanged from the current branch state (byte-identical, confirm with a diff before/after this task).
7. `pytest tests/unit` still passes (this task shouldn't be able to break it, since the exception hierarchy itself isn't touched — but confirm).
8. Regression gate passes: `applypilot status` and `applypilot run discover enrich score` behave identically to `main` (this is the real test that the revert was clean).

## Forbidden Changes

- Do not modify anything under `src/ultron_jobs/core/exceptions/` or its tests.
- Do not re-add any of the reverted functionality, even partially, even "just the useful part."
- Do not modify any file not explicitly named in Sections A–C above.
- Do not open a new architectural discussion in the PR description — if something
  seems worth reconsidering, name it as an open question for the architect, don't
  act on it here.

## Definition of Done

- [ ] All Section A files byte-identical to `main`.
- [ ] All Section B files deleted (with debug-script content preserved somewhere
      recoverable, not silently lost, if it has diagnostic value).
- [ ] All Section C files relocated via `git mv` (history preserved).
- [ ] Section D files confirmed untouched.
- [ ] All Acceptance Criteria pass.
- [ ] Regression gate confirmed.
- [ ] PR description includes: the `git diff --stat` proving the final diff only
      touches what this task authorized, plus a short note on where the deleted
      debug scripts' content went (if kept) or confirmation nothing of value was lost.
