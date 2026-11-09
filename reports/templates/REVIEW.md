# Review: <title>

- Status: ready_for_review | changes_requested | approved_for_merge | blocked
- Date: YYYY-MM-DD
- Slug: <slug>
- Plan: reports/plan-<slug>.md
- Implementation: reports/implementation-<slug>.md
- Testing: reports/testing-<slug>.md
- PR: <URL or pending>

## Plan-to-result traceability

| Approved criterion | Implemented evidence | Test evidence | Review result |
| --- | --- | --- | --- |
| <criterion> | <file/API> | <test report item> | pass/fail/open |

## Findings

Each finding is mandatory and must remain in this report even after a fix.

| ID | Severity | Status | Evidence | Impact | Required resolution | Retest evidence |
| --- | --- | --- | --- | --- | --- | --- |
| R-001 | P0/P1/P2/P3 | open/resolved/accepted_by_user | <file:line, command or scenario> | <user/business/security impact> | <specific required change> | <command, UI scenario or link> |

Review independently: do not accept implementation/test report claims without
checking approved plan, complete diff (including untracked files), relevant
code, migration/API/Admin behaviour and evidence. Record scope creep,
unapproved UX, missing proof and design-system inconsistencies as findings.

## User review checklist

## Merge/deploy decision

## Follow-ups

Merge or deploy is forbidden unless all approved criteria are resolved and the
user explicitly accepts the review result.
