# Project harness

`harness/` is short active context, not project memory or documentation dump.

## Reading order

1. Read root `AGENTS.md`.
2. For non-trivial work, read `docs/project/current-state.md`.
3. If task exists, read `harness/tasks/active/<slug>.md` and its approved plan.
4. Read only documents/ADRs/code linked by that task. Use `ast-index` before
   code-structure search.

## Update rules

- Before creating or continuing a feature branch, update remote references and
  verify that its base is the current `origin/main`. Do not continue a branch
  from a historical `main`; rebase or merge the current `main` first and
  resolve conflicts deliberately.
- New client scope: classify questions vs changes; group related changes.
- New change group: create an active task card and a draft plan report.
- Requirement correction: update same draft plan and its revision log first.
- Approved plan: set plan status to `approved`, then implement.
- Frontend objective without explicit UI behaviour: stop at draft plan. Record
  pages, states, copy, navigation, desktop/mobile behaviour and unchanged
  areas; wait for user approval before changing frontend code.
- Before review, use `reports/README.md` as a role change: reviewer starts
  from approved plan and full diff, not from author's conclusion. Every
  finding belongs in the review report.
- Material discovery for active task: add concise fact/evidence to
  `context/active/<slug>.md`.
- Completion: archive task card as a short pointer. Promote only durable facts
  to `docs/` or an ADR.

Never place secrets, customer data, raw logs or copied source files here.
Multica owns task status; local task cards link to it.
