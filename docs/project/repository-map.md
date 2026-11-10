# Repository map

- Last verified: 2026-11-08
- Evidence: `rg --files`, `ast-index.cmd map`, root manifests
- Owner: agent; update with source changes

| Area | Purpose | Documented here? |
| --- | --- | --- |
| `frontend/` | React/Vite public web client | `architecture/components.md`, `api/contracts.md`, existing design docs |
| `backend/main_service/` | Django primary API, Admin, booking and account domain | architecture/API/product/operations docs |
| `backend/recommendation_service/` | FastAPI recommendation API and worker | architecture/API/operations docs |
| `backend/assistant_service/` | Django RAG/chat service | architecture/API/operations docs |
| `backend/vectorizer/` | Celery vectorisation worker | architecture/operations docs |
| `backend/nginx/` | Local proxy configuration | `operations/local-stack.md` |
| `backend/docker-compose.yml` | Development stack | `operations/local-stack.md` |
| `backend/compose.production.yml` | Production Compose topology | `operations/production.md` |
| `frontend/public/` | Published images, icons and legal downloads | `architecture/components.md` |
| `examples/` | Sample input material | this document |
| `docs/` | Durable project documentation | `docs/INDEX.md` |
| `harness/` | Active task context | `harness/README.md` |
| `reports/` | Plan/implementation evidence | `reports/README.md` |
| `.github/` | PR template/workflows, if tracked | `development/testing.md` |
| `.codex/`, `.agents/` | Project agent skills/instructions | `development/documentation-policy.md` |
| `.vscode/`, `.worktrees/`, `node_modules/`, `.git/` | Local/editor/generated/Git state | not documentation sources |

Root `README.md` is repository entry point. `frontend/README.md` is Vite
template text and is not product documentation. Never document or commit real
`.env`, certificates, model binaries, caches or runtime volumes.

`examples/excursions.txt` is input material only; verify its data before using
it to seed any environment.
