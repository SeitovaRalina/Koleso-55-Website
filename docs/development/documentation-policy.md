# Documentation policy

- Last verified: 2026-11-08
- Evidence: `AGENTS.md`, `harness/README.md`, `reports/README.md`
- Owner: author of affected change

## Canonical locations

| Information | Location |
| --- | --- |
| Durable facts and architecture | `docs/` |
| Active task scope/discoveries | `harness/` |
| Plan and delivery evidence | `reports/` |
| Issue status/assignee | Multica |
| Source-level truth | code, schema and configuration |

Every durable document records `Last verified`, evidence and owner. Use links
instead of copying another document or source body. Mark unknowns/conflicts;
never turn inference into fact.

Product/code/API/migration/Admin/runtime/UI work needs plan + implementation +
testing + review evidence before merge/deploy. Documentation-only/low-risk work
needs plan + implementation; testing/review is risk- or request-based.

Do not put secrets, customer data, raw logs, private hostnames, certificates,
environment values or binary contents in docs. Generated output must state its
source and generation date. Add an ADR only for an important durable decision.
