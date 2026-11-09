# Multica integration

Multica is the source of truth for task status, assignee and PR link. This
repository is the source of truth for code, plans, evidence and long-lived
documentation. Synchronise the project description and agent instructions in
Multica manually from this file and root `AGENTS.md`; never place credentials,
private hosts, tokens or customer personal data in Multica.

## Project description

`Колесо путешествий 55` — site for travel programmes and excursions: React /
Vite frontend, Django/DRF main API and supporting recommendation service. One
Multica task has one observable outcome. Work is reviewed by a human; an agent
does not mark a task `done`.

## Agent instructions for Multica

1. Read `AGENTS.md`, then `harness/README.md`,
   `docs/project/current-state.md`, the active task card and only relevant
   linked documents. Use `ast-index` before structural code search; use the
   React skill for frontend work.
2. Before changing product code, create or update a `reports/plan-<slug>.md`.
   Implement only after explicit user approval and `Status: approved`.
   After implementation create implementation, testing and review reports when
   required by `AGENTS.md`.
3. Update remote refs before creating a branch. Base new branches on current
   `origin/main`; do not continue a historical branch without first rebasing or
   merging current `main` deliberately.
4. Use the main checkout for one sequential task. Create a Git worktree only
   when Multica runs genuinely parallel tasks. Use the project's existing
   `feature/KOLE-<number>-<slug>` or `fix/KOLE-<number>-<slug>` naming style;
   do not use `agent/...` as a PR head branch.
5. Keep change scope minimal. Update migrations, API contracts, `.env.example`
   and durable docs when the change requires them. Do not read or publish real
   `.env` values, secrets or production coordinates.
6. For UI, prove desktop and mobile behaviour with real browser screenshots.
   For backend, add happy/error/boundary tests and migration/API evidence.
   Attach evidence to the PR; do not claim an unrun check passed.
7. Do not merge, deploy or alter production without an explicit task and
   approval. Production tasks must follow `docs/operations/production.md` and
   local-only handover rules.
8. If customer information is required, ask concise numbered questions in the
   same task, complete independent work, set only that task `blocked`, then
   resume it after an answer.

## Task lifecycle

- Group small related defects by one user-visible flow; isolate unrelated or
  risky changes.
- Status flow: `backlog` → `in_progress` → `in_review` → human `done`.
  Use `blocked` only for a concrete external decision/access blocker.
- Put an active local task card in `harness/tasks/active/` with the Multica
  key/link, plan and evidence links. Multica stores workflow state; the local
  card stores only scope and durable decisions.
- For every code task, prepare a PR description with scope, acceptance
  criteria, actual checks, screenshots or API evidence, remaining risks and
  manual verification. If GitHub access is unavailable, keep the branch and
  report the exact blocker.
