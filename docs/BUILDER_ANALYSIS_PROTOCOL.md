# Builder Analysis Protocol

Status: ACTIVE
Applies to: every builder (Antigravity, Codex, Windsurf, Copilot) on every task
Referenced by: all `docs/tasks/F#-##-*.md` files

## Why this exists

Builders are handed narrow, well-scoped tasks (Files Allowed, Forbidden Changes,
Acceptance Criteria) so they can't wander. That scoping only works if the builder
actually understands the code it's about to touch — not just the task file in
isolation. A builder that writes code against its assumption of what a file
contains, instead of what the file actually contains, produces subtly wrong work
even when it follows every explicit instruction correctly.

This protocol is a mandatory gate: **no implementation code until the analysis
step below is complete and its output exists as a written artifact.** This is not
about slowing things down for its own sake — it's the cheapest place to catch a
wrong assumption, before it's baked into code and tests.

## When this applies

Every task, every time. No exceptions for "small" tasks — small tasks with wrong
assumptions are exactly how scope violations happen quietly.

## The Analysis Phase (mandatory, before writing any code)

### Step 1 — Re-read governing context
Read, in full, not skimmed:
- `ULTRON_JOBS_MASTER_SPEC.md` (or the current architecture docs if the master
  spec doesn't exist yet) — sections relevant to this task's layer.
- The specific task file (`docs/tasks/F#-##-*.md`) — Objective through
  Definition of Done, all of it, including Forbidden Changes.
- Any ADRs referenced by the task, in full.

### Step 2 — Read every file the task touches, and everything that touches them
- Every file listed under **Files** / **Files Allowed** in the task — read the
  entire file, not just the function being modified.
- Every file that imports from, or is imported by, those files. Use `grep`/search
  for the module/class names, don't rely on memory of what "should" be there.
- Any existing tests covering this code, passing or not.
- If the task touches a file the builder has not personally read in this session,
  it has not been analyzed — re-reading a summary from a prior task file does not
  count.

### Step 3 — Identify issues before proposing solutions
For each file/area read, explicitly note:
- **Current behavior**: what the code actually does today (not what the docs say
  it should do — flag any mismatch between docs and reality).
- **Risks**: what could break if this area is touched (callers, side effects,
  shared state, migration concerns).
- **Open questions**: anything genuinely ambiguous that the task file doesn't
  resolve. These get raised before coding starts, not discovered mid-implementation.

### Step 4 — Produce the Analysis Report
Before writing any code, the builder produces a short written artifact — either
at the top of the PR description or as `docs/tasks/F#-##-analysis.md` — containing:

```markdown
## Analysis Report — F#-##

### Files read in full
- <path> — <one-line summary of what it actually does>
- ...

### Callers / dependents identified
- <path> calls <thing> — <why it matters for this task>

### Discrepancies found (docs vs. actual code)
- <none, or specific mismatches>

### Risks / edge cases this task could affect
- ...

### Open questions (if any) — raised before implementation begins
- ...

### Proposed approach
<2-5 sentences: how the builder intends to satisfy the Acceptance Criteria given
everything above>
```

### Step 5 — Gate
Implementation does not begin until the Analysis Report exists and has been
reviewed (by the architect, in chat or PR comment) — unless the task file
explicitly marks itself exempt (rare; reserved for trivial scaffolding tasks
with no existing code to misread).

If Step 3 surfaces something that contradicts the task's Constraints or
Forbidden Changes, the builder stops and flags it rather than resolving the
contradiction on its own judgment. Redesigning around a discovered problem is
an architecture decision, not a builder decision.

## Notes for Flash-tier / fast builder models specifically

This protocol is written as an explicit checklist rather than general guidance
on purpose. Faster, cheaper models are more prone to pattern-matching a task to
something similar seen in training and skipping the "read what's actually here"
step, especially over long context. Two things help:

- Keep task files short and single-concern (already policy) — the Analysis
  Report should reference a small, bounded file set, not "the whole repo."
- Require the Analysis Report as a **separate output before code**, not folded
  into the same pass as implementation. Asking for analysis-then-code in one
  shot lets a fast model rationalize past the analysis; asking for analysis as
  a standalone deliverable that gets reviewed first creates an actual checkpoint.

## Relationship to existing process

This slots into the existing lifecycle (Requirement → Research → Architecture →
Review → Sprint → Task Breakdown → **Implementation**) as the first sub-step of
Implementation, not a new top-level stage. It does not replace the regression
gate (`applypilot status`, `applypilot run discover enrich score`), which still
runs after implementation, before merge.
