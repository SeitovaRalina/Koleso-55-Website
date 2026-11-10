# Current state

- Last verified: 2026-11-08
- Evidence: repository `main` at `3272631`; `AGENTS.md`; Compose manifests
- Owner: agent updates only after direct evidence

## Verified facts

- Repository root branch at verification: `main`.
- Local working tree contains uncommitted documentation/workflow material.
  Treat it as local work, not deployed state.
- Primary services and commands are listed in root `AGENTS.md`.
- Production/deployment assumptions must be checked against
  `docs/operations/production.md` before any release.

## Unknown until checked for a task

- Current running local containers and their health.
- Current production commit and migrations.
- Multica issue status and PR state.

## Documentation conflicts to resolve deliberately

- Root `AGENTS.md` describes Django 5, while
  `backend/main_service/pyproject.toml` currently requires Django 6. Treat
  manifests/runtime as dependency evidence; do not change either statement
  without an approved compatibility task.
- `frontend/README.md` remains Vite starter text and is not a product guide.

Do not replace an unknown with an inference. Add task-specific discoveries to
`harness/context/active/<slug>.md`; promote only durable facts to this file.
