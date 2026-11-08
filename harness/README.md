# Project harness

`harness/` is short active context, not project memory or documentation dump.

## Reading order

1. Read root `AGENTS.md`.
2. For non-trivial work, read `docs/project/current-state.md`.
3. If task exists, read `harness/tasks/active/<slug>.md` and its approved plan.
4. Read only documents/ADRs/code linked by that task. Use `ast-index` before
   code-structure search.

## Update rules

- New client scope: classify questions vs changes; group related changes.
- New change group: create an active task card and a draft plan report.
- Requirement correction: update same draft plan and its revision log first.
- Approved plan: set plan status to `approved`, then implement.
- Material discovery for active task: add concise fact/evidence to
  `context/active/<slug>.md`.
- Completion: archive task card as a short pointer. Promote only durable facts
  to `docs/` or an ADR.

Never place secrets, customer data, raw logs or copied source files here.
Multica owns task status; local task cards link to it.
