# Plan: project documentation harness

- Status: approved
- Date: 2026-11-08
- Slug: memory-bank-harness (legacy filename; chosen structure is `harness/`, not `.memory-bank/`)
- Owner: user and agent
- Approval: user explicitly approved in Codex chat, 2026-11-08

## Revision log

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-08 | Draft created | Initial proposal: `.memory-bank/` |
| 2026-11-08 | Draft updated | User challenged one-folder model; research supports split `docs/ + harness/ + reports/` |
| 2026-11-08 | Approved | User approved revised `docs/ + harness/ + reports/` plan |

## Goal

Create a versioned, concise project harness that lets any future agent separate
verified facts from proposals, find current task quickly and avoid unapproved
implementation without loading irrelevant history into context.

## Current state and evidence

- `AGENTS.md` is the root instruction source.
- `docs/` contains detailed product, deployment and integration documentation.
- `reports/` now contains lifecycle evidence for plan, implementation, testing
  and review, with templates under `reports/templates/`.
- There is no project-wide current-state index, decision log or task registry.

## Research basis

- OpenAI’s harness guidance recommends a short `AGENTS.md` as a map, while
  structured repository docs remain the system of record. A giant always-loaded
  manual causes context dilution and rapid staleness.
- VS Code’s context-engineering guide recommends progressive disclosure,
  context isolation by work type and versioned context rather than a complete
  context dump for every task.
- Keep architecturally significant decisions as lightweight, versioned Markdown
  ADRs; use numbered records with status and a link when superseded.
- Document architecture in layers rather than a single large diagram: system
  context, containers and only the components that need explanation.
- Record phase/task context only when omitting it could change an approved
  approach or make a future agent repeat material discovery. Link to canonical
  evidence instead of copying plans, source code or test output.

## In scope

Create three purpose-separated root areas. Do **not** create `.memory-bank/`:
name suggests opaque agent-only storage and invites one large stale archive.
Stable facts live in `docs/`; active, task-scoped orientation lives in
`harness/`; lifecycle evidence lives in `reports/`.

```text
AGENTS.md                             # short policy + reading map, never encyclopedia
docs/                                 # durable, human-readable source of truth
  INDEX.md                            # navigation and reading routes
  project/
    overview.md                       # product purpose and durable business constraints
    current-state.md                  # verified present state and freshness evidence
  product/
    backlog.md                        # curated priorities; Multica owns execution status
  architecture/
    context.md                        # system context / external dependencies
    containers.md                     # frontend, Django, DB, infrastructure
  adr/                                # immutable numbered significant decisions
  operations/                         # deploy, backup, incident runbooks
  api/                                # contracts not already discoverable from schema
harness/                              # short, active agent-work context only
  README.md                           # reading order and update rules
  tasks/
    templates/task.md
    active/<slug>.md                  # scope, status, decisions, report/PR links
    archive/                          # compact completed task records only
  context/
    active/<slug>.md                  # material discoveries for an approved task
reports/                              # plan → implementation → testing → review evidence
```

`docs/` folders are introduced only when a canonical document is missing; the
existing relevant documentation is migrated gradually rather than duplicated.

The agent reads context progressively:

| Tier | Read when | Maximum purpose |
| --- | --- | --- |
| 0 | every task | `AGENTS.md`: policy, commands, pointers |
| 1 | every non-trivial task | `docs/project/current-state.md`, `harness/README.md`, active task index |
| 2 | a named/active task | its task file, approved plan and active task context |
| 3 | implementation/review | only target module docs, ADRs, API contract and code found via `ast-index` |

No agent reads whole `docs/`, `harness/`, reports or archives by default.

Initial `harness/` structure:

```text
harness/
  README.md
  tasks/templates/task.md
  tasks/active/
  tasks/archive/
  context/active/
  templates/
    active-context.md
```

Define clear ownership to prevent duplicate or stale documentation:

| Information | Canonical location | Memory-bank role |
| --- | --- | --- |
| Agent rules | `AGENTS.md` | link and startup checklist |
| Product/current/architecture/deploy/API facts | `docs/` | canonical source of truth |
| Per-change evidence | `reports/` | immutable lifecycle evidence |
| Architectural decisions | `docs/adr/` | numbered, immutable ADR |
| Active task state and discoveries | `harness/tasks/active/`, `harness/context/active/` | short links and material task context |
| Product backlog | `docs/product/backlog.md` | priority snapshot; Multica owns task execution status |

## Operating rules

1. Every current-state, task and active-context file carries `Last verified`,
   `Evidence` and `Owner` metadata.
2. Facts, proposals and unknowns are labelled separately; an agent may not turn
   a proposal into a fact without evidence or an approved plan.
3. At task start, read `AGENTS.md`, `harness/README.md`,
   `docs/project/current-state.md`, relevant task file and only linked ADRs.
4. Before implementation, the task file must link to an `approved`
   `reports/plan-<slug>.md`.
5. After implementation/testing/review, update only affected docs and harness files
   and link all four lifecycle reports. `context/active/` records only material
   discoveries; archive or distil it when the task is completed.
6. Never rewrite historical ADRs; mark them superseded with a link to the
   replacement.
7. Do not place secrets, customer data, raw production logs or private IPs in
   `docs/`, `harness/` or `reports/`.
8. `docs/project/current-state.md` records commit or PR and date that last verified each
   statement. Stale/unknown entries are explicit rather than guessed.
9. Add a lightweight validation script later: front-matter present, links exist,
   active task has an approved plan before implementation, and no obvious secret
   files were placed in the memory bank. Make it a CI gate only after it is
   proven locally.

## Out of scope

- Replacing `docs/`, GitHub issues, PRs or Multica.
- Auto-generating documentation from unverified code or writing a large UML
  model that nobody maintains.
- Storing secrets, personal data or production access details.

## Acceptance criteria

- A new agent can orient itself in five minutes using the specified reading
  order and distinguish verified state from planned work, without reading old
  task details.
- Every active task links to its plan/report lifecycle and acceptance criteria.
- Significant decisions have an ADR with context, alternatives, decision and
  consequences.
- The structure has templates and a freshness policy, not only empty folders.
- Existing documentation is linked, not copied wholesale; `.memory-bank/` stays
  short enough to be a useful task entry point.

## Verification plan

- Inspect all links and run a repository search to ensure no secrets or `.env`
   values entered the new documentation areas.
- Create one representative task record, one active context record and one ADR
  for this harness.
- Review the agent startup checklist against `AGENTS.md` and reports harness.
- Ask the user to review the generated directory tree and initial current-state
  summary before treating it as authoritative.

## Risks and rollback

- Too much duplicated text can become stale; mitigate with canonical-location
  mapping and short indexes.
- Overly frequent mandatory updates can slow small fixes; only update memory
  files affected by the change, while reports remain mandatory for product work.
- Rollback is safe: `harness/` is additive, versioned Markdown.

## Open decisions

1. Should active task files always mirror a Multica key when one exists, or use
   a local ID alongside it?
2. Should completed task records stay in Git under `harness/tasks/archive/` forever, or
   be summarised quarterly while reports remain the permanent evidence?

## Worked example: client sends a batch of bugs and questions

Input: client sends ten mixed items: two questions, six bugs, one copy change
and one new feature request.

1. Agent answers factual questions from existing behaviour. No task or code
   change unless an answer reveals a defect.
2. Agent groups remaining items by shared user flow and risk. Example groups:
   `catalog-filters`, `booking-and-requests`, `admin-content`, `site-seo`.
3. For each group, create a short `harness/tasks/active/<slug>.md` containing:
   Multica key/link, outcome, non-goals, affected paths discovered via
   `ast-index`, open questions, dependencies and links to reports.
4. Agent writes `reports/plan-<slug>.md` in `draft`. It covers scenario, data,
   API, statuses, Admin, UX, migrations, tests, screenshots and acceptance
   criteria. It does not change product code.
5. User corrects requirement, for example: “keep sidebar filters; move only
   categories to sticky header.” Agent immediately amends same draft plan,
   records revision/date and shows changed acceptance criteria. No coding.
6. User explicitly approves plan. Agent changes plan status to `approved`, then
   implements only that group. Separate unrelated group stays queued.
7. Agent creates implementation/testing/review reports, updates task card with
   outcome and evidence, then asks user for review. Merge/deploy happens only
   after required reports and user review.
8. On completion, task card becomes a short archive pointer; durable discovery
   goes to `docs/` or an ADR only if it changes future project decisions.

## Approval record

Awaiting explicit user approval. Do not create the `.memory-bank/` structure
until this plan is approved.
