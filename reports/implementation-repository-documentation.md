# Implementation: complete repository documentation

- Status: implemented
- Date: 2026-11-08
- Slug: repository-documentation
- Approved plan: `reports/plan-repository-documentation.md`
- Branch / PR: `main` working tree; no PR created

## Delivered scope

- Reworked `docs/INDEX.md` into progressive reading routes.
- Added project map and local-development documentation.
- Documented system context, component ownership, data flows and integrations.
- Added API route/contract inventory for Django, recommender and assistant.
- Added product/Admin ownership map without duplicating business decisions.
- Added operations runbooks for local stack, production topology, migrations and
  jobs.
- Added development/testing/documentation policy.
- Updated lifecycle policy: testing/review reports are risk-based for
  documentation-only work, but mandatory for product/code/API/migration/Admin,
  runtime/UI, merge and deploy work.
- Migrated useful legacy guidance into component-oriented docs and removed
  superseded root-level documentation files and obsolete HTML concepts.

## Legacy migration map

| Removed legacy material | New canonical location |
| --- | --- |
| Agent workflow and Multica instructions | `docs/development/workflow.md`, `docs/development/multica.md`, root `AGENTS.md` |
| Backend integration plan | `docs/architecture/*`, `docs/api/contracts.md`, `docs/operations/*` |
| Django Admin guide | `docs/product/admin-content.md` |
| Frontend design system and UI direction | `docs/product/design-system.md` |
| Product decisions / development questions / next steps | `docs/product/business-rules.md`, `open-questions.md`, `backlog.md` |
| YooKassa plan | `docs/product/payments.md` |
| Production handover/readiness/redeploy/Timeweb docs | `docs/operations/production.md`, `local-stack.md`, `migrations-data.md`, `jobs-observability.md` |
| Historical HTML card/filter concepts | `docs/product/visual-references.md` |

## Full legacy-file migration map

| Legacy file | Status | Canonical replacement / disposition |
| --- | --- | --- |
| `docs/AGENT_HANDOVER.md` | deleted | Safe production rules → `docs/operations/production.md`; private hosts, SSH paths, production IPs and unrelated-service details deliberately not migrated. |
| `docs/AI_AGENT_WORKFLOW.md` | deleted | `AGENTS.md`, `docs/development/workflow.md`, `docs/development/multica.md`, `harness/README.md`, `reports/README.md`. |
| `docs/BACKEND_INTEGRATION_PLAN.md` | deleted | `docs/architecture/components.md`, `data-flows.md`, `integrations.md`, `docs/api/contracts.md`, `docs/operations/local-stack.md`. |
| `docs/DEVELOPMENT_QUESTIONS.md` | deleted | Answered decisions → `docs/product/business-rules.md`; unresolved items → `docs/product/open-questions.md`. |
| `docs/DJANGO_ADMIN_GUIDE.md` | deleted | Ownership, content areas and access boundaries → `docs/product/admin-content.md`; technical behaviour remains code/Admin source. |
| `docs/FRONTEND_DESIGN_SYSTEM.md` | deleted | Tokens, visual direction, UI-kit and UX rules → `docs/product/design-system.md`; component ownership → `docs/architecture/components.md`. |
| `docs/MULTICA_AGENT_INSTRUCTIONS.md` | deleted | `docs/development/multica.md` and `docs/development/workflow.md`. |
| `docs/MULTICA_PROJECT_DESCRIPTION.md` | deleted | Product/repository overview → `docs/project/overview.md`; task policy → `AGENTS.md` and `harness/README.md`. |
| `docs/NEXT_STEPS.md` | deleted | Current priority snapshot → `docs/product/backlog.md`; future work needs a Multica task and approved plan. |
| `docs/PRODUCT_DECISIONS.md` | deleted | `docs/product/business-rules.md`, `payments.md`, `design-system.md`, `open-questions.md`. |
| `docs/PRODUCTION_OPERATIONS.md` | deleted | `docs/operations/production.md`, `local-stack.md`, `jobs-observability.md`, `migrations-data.md`. |
| `docs/PRODUCTION_READINESS_PLAN.md` | deleted | Readiness checklist distilled into `docs/operations/production.md`; dated execution checklist intentionally not retained as current truth. |
| `docs/REDEPLOYMENT_AND_HANDOVER_PLAN.md` | deleted | Release safety/backup/health guidance → `docs/operations/production.md`; historical incident detail intentionally omitted. |
| `docs/TIMEWEB_NGINX_DEPLOY.md` | deleted | Portable topology/proxy/TLS boundary → `docs/operations/production.md` and `local-stack.md`; provider-specific hosts, sample credentials and stale sizing claims omitted. |
| `docs/YOOKASSA_IMPLEMENTATION.md` | deleted | Product/payment invariants → `docs/product/payments.md`; detailed future design must be recreated as approved task plan when implementation starts. |
| `docs/catalog-filter-concept.html` | deleted | Superseded visual artefact; status/policy → `docs/product/visual-references.md`. |
| `docs/event-card-concepts.html` | deleted | Superseded visual artefact; status/policy → `docs/product/visual-references.md`. |

## Files changed

- `AGENTS.md`, `docs/AI_AGENT_WORKFLOW.md`, `reports/README.md`
- `docs/INDEX.md`, `docs/project/*`, `docs/architecture/*`, `docs/api/*`
- `docs/product/*`, `docs/operations/*`, `docs/development/*`
- `reports/plan-repository-documentation.md`

## Data migrations and backfill

None. Documentation-only change.

## API and Admin contract

No behaviour changed. Inventory documents actual routes. Two existing
source-level discrepancies are explicitly recorded, not fixed:

1. booking route is protected in frontend while product rule says guest booking;
2. frontend has a slot API helper for a route absent from current Django URLs.

## Deliberate deviations from approved plan

None. The plan's revised component-oriented structure was followed: no
top-level `docs/backend/` or `docs/frontend/` trees were created.

## Known limitations and follow-ups

- Existing historical documents were linked rather than blindly rewritten.
- Production component enablement remains unknown without direct server checks.
- Source-level discrepancies need separately approved product/code tasks.

## Handoff

This is documentation-only/low-risk work. Per approved policy, separate
testing/review reports are not required unless user requests merge/deploy or a
documentation validation risk appears.
