# Plan: complete repository documentation

- Status: approved
- Date: 2026-11-08
- Slug: repository-documentation
- Owner: user and agent
- Approval: user explicitly approved revised plan in Codex chat, 2026-11-08

## Revision log

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-08 | Draft created | Initial complete-documentation proposal |
| 2026-11-08 | Draft revised | Research and user feedback: remove top-level `backend/` and `frontend/`; organise by questions and deployable components |
| 2026-11-08 | Approved | User approved revised information architecture |
| 2026-11-08 | Approved scope expansion | User requested migration of useful legacy docs into new structure and removal of superseded files after a file-by-file migration map |

## Goal

Turn `docs/` into concise, verifiable navigation for every maintained
repository area. It must explain ownership, boundaries, entry points, data/API
contracts, local operation and tests without copying source code or secrets.

## Audit evidence

- `ast-index.cmd update`, `map`, `conventions`, `search` ran on 2026-11-08.
- Indexed code: Python/TypeScript; 229 indexed files.
- Repository top-level areas: `backend/`, `frontend/`, `examples/`, `docs/`,
  `harness/`, `reports/`, project-local `.codex/`, `.agents/`, `.github/`,
  `.vscode/` and `.worktrees/`.
- Runtime/application areas discovered:
  - Django `main_service`: accounts, excursions, bookings, reviews, wishlist,
    analytics;
  - FastAPI `recommendation_service`: recommendations, similar, admin,
    Redis/RabbitMQ/PostgreSQL integrations;
  - Django `assistant_service`: chat/RAG, Chroma persistence, management
    commands;
  - `vectorizer`: Celery worker for vectorisation;
  - React/Vite `frontend`: pages, router, API client, UI/layout/catalog/home
    components, auth context, styling and public assets.
- Docker Compose defines Postgres, Redis, RabbitMQ, main service, two Django
  Celery processes, recommender API/worker, assistant service, vectorizer and
  optional nginx proxy.

## Scope

### Documentation information architecture

```text
docs/
  INDEX.md                              # reading routes and ownership
  project/
    overview.md                         # product, repository boundaries
    current-state.md                    # dated, evidence-backed current facts
    repository-map.md                   # every maintained top-level/folder area
    local-development.md                # prerequisites, safe start/stop commands
  architecture/
    context.md                          # people/systems and trust boundaries
    containers.md                       # deployable containers and ownership
    components.md                       # frontend + all services in one component map
    data-flows.md                       # booking, requests, analytics, recommendations, assistant
    integrations.md                     # Redis/RabbitMQ/Postgres/LLM/YooKassa boundaries
  api/
    README.md                           # source of truth and generated-vs-handwritten rule
    contracts.md                        # all HTTP contracts, grouped by owning component
  product/
    README.md                           # source-of-truth map
    business-rules.md                   # links to accepted decisions, no stale duplicates
    admin-content.md                    # what Django Admin manages
    backlog.md                          # priority snapshot; Multica status stays canonical
  operations/
    README.md                           # runbook map
    local-stack.md                      # Compose topology and health checks
    production.md                       # link/align existing handover and deployment docs
    migrations-data.md                  # schema/seed policy and rollback boundaries
    jobs-observability.md               # Celery queues, logs, health, backup links
  development/
    README.md                           # contributor/agent entry
    testing.md                          # test layers, exact commands, evidence rules
    documentation-policy.md             # freshness, ownership, generated docs policy
  adr/
    README.md                           # ADR convention/index
```

Useful content from legacy specialised documents is migrated into this
information architecture. After a file-by-file migration map and link update,
superseded legacy files are deleted rather than left as competing sources of
truth. Historical concept HTML is retained only when it is explicitly marked as
a visual reference; otherwise it is removed as obsolete artifact.

### Folder coverage matrix

| Repository area | Documentation location | Required content | Excluded |
| --- | --- | --- | --- |
| Root files | `docs/project/repository-map.md` | `README`, `AGENTS`, package metadata, entry rules | secrets and lockfile dumps |
| `frontend/` | `docs/architecture/components.md`, `docs/development/testing.md`, existing design docs | routes, pages, API client, state/layout, build/test, assets | component source/props copied verbatim |
| `backend/main_service/` | `docs/architecture/components.md`, `docs/api/contracts.md`, `docs/product/admin-content.md` | Django apps, models, Admin, URL modules, Celery, migrations/testing | migrations copied line by line |
| `backend/recommendation_service/` | components/API/operations docs | router contracts, models, dependencies, worker, migrations/tests | model binary content |
| `backend/assistant_service/` | components/API/operations docs | RAG pipeline, chat storage, commands, Chroma persistence | API keys, prompt/database contents |
| `backend/vectorizer/` | components/operations docs | queue, inputs/outputs, retry/failure boundary | task code dump |
| `backend/nginx/`, compose files, cert placeholders | `docs/operations/*` | ports, proxy boundary, profiles, health checks | live hostnames, certificates, env values |
| `frontend/public/` | `docs/architecture/components.md` and design docs | asset/document role, publishing policy | binary asset contents |
| `examples/` | `docs/project/repository-map.md` | purpose and safe usage | customer/sample personal data |
| `.github/` | `docs/development/testing.md` | PR/CI workflow if present | generated workflow logs |
| `.codex/`, `.agents/` | `docs/development/documentation-policy.md` | skill/instruction discovery and scope | agent cache/private config |
| `.vscode/`, `.worktrees/`, `node_modules/`, `.git/` | repository map | explicitly runtime/local, not project docs source | contents |
| `harness/`, `reports/` | `docs/development/documentation-policy.md` | lifecycle and retention rules | report duplication |

## Method

1. Build a folder/file inventory excluding `.git`, `node_modules`, runtime
   volumes, env files, certificates and binaries.
2. Use `ast-index` before each code-structure query. For each service map entry
   points, routers/URLs, models, background jobs, tests and external calls.
3. Map every legacy document to target document(s). Compare findings with current
   documentation. Label conflicting or unverified statements; do not silently
   overwrite production instructions.
4. Create index documents first, then component/API/operations docs.
   Each statement carries source paths and a `Last verified` date.
5. Add cross-links. One fact has one canonical home; replace legacy links and
   delete mapped superseded documents only after their target content exists.
6. Run Markdown link/path validation, docs-inventory validation and relevant
   source checks only where documentation discovers a source mismatch.
7. Create implementation, testing and review reports. Review with user before
   any merge/deploy.

## User scenarios

### New agent gets a catalogue bug

Reads `AGENTS.md` → `docs/project/current-state.md` → active task card →
`docs/architecture/components.md` and `docs/api/contracts.md` → searches exact code
symbols via `ast-index`. It does not load assistant/RAG or old report history.

### Agent changes an Admin workflow

Reads active task → `docs/architecture/components.md` →
`docs/product/admin-content.md` → related Django app/model/Admin source. It
updates durable Admin documentation only after implementation evidence.

### Production release agent

Reads `docs/operations/production.md`, `docs/AGENT_HANDOVER.md`, approved
review report and exact service docs. It does not use stale `NEXT_STEPS.md` as
deployment instruction.

## Data, API, migrations and Admin impact

Documentation-only. No data migration, API or Admin behaviour changes.
Documentation may expose contradictions; those become separate draft tasks,
not incidental code fixes.

## Tests and acceptance criteria

- Every maintained repository area in coverage matrix has a canonical document
  or an explicit “local/generated/not documented” classification.
- `docs/INDEX.md` routes a new agent to correct document within two clicks.
- No doc includes `.env` values, production credentials, private addresses,
  certificates, raw logs, binary dumps or customer data.
- Service/API docs name actual source entry points and are checked against
  `ast-index` findings.
- Existing canonical docs are linked rather than copied wholesale.
- Markdown links and referenced repository paths validate locally.
- Final reports include exact audit/check commands and unresolved conflicts.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| “Fully document” becomes stale code mirror | Document contracts, ownership and entry points; link source. |
| Historical docs conflict with current code | Mark conflict/evidence; open separate task, do not guess. |
| Sensitive config leaks | Use `.env.example` names only; never read/copy real `.env` values. |
| Scope too large for one unreviewed batch | Deliver in reviewable layers: indexes → services/APIs → operations/development. |
| New agent reads everything | Enforce progressive reading map in `AGENTS.md` and indexes. |

## Open decisions

1. Should assistant/recommender/vectorizer remain first-class documented
   production components, or be marked experimental/disabled after direct
   operational verification?
2. Is `docs/api/*.md` sufficient as hand-maintained inventory, or should a
   future task generate OpenAPI snapshots from running services?
3. Should existing historical plans be retained as reference or marked stale
   when they conflict with `current-state.md`?

## Approval record

Awaiting explicit approval. Do not mass-create or rewrite documentation until
this scope is approved.
