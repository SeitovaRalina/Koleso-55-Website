# Review: unified guest request linking

- Status: changes_requested
- Date: 2026-11-09
- Slug: unified-guest-request-linking
- Plan: reports/plan-unified-guest-request-linking.md
- Implementation: reports/implementation-unified-guest-request-linking.md
- Testing: reports/testing-unified-guest-request-linking.md
- PR: pending

## Review method

- Compared all staged and unstaged production changes against the approved
  plan and its revision log.
- Read ownership, account verification, request API, Admin, migration and
  frontend account flows.
- Re-ran focused checks listed in the linked testing report and inspected
  desktop/mobile local UI state.

## Plan-to-result traceability

| Approved criterion | Implemented evidence | Test evidence | Review result |
| --- | --- | --- | --- |
| Three request types in `Мои заявки`, newest first | account API/types/UI | 29 Django tests include ordering and account isolation | pass |
| Immediate ownership for authenticated sender | create views | local UI/API check | pass |
| Safe verified-email guest claiming | shared claim service + tests | isolated HTTP + fresh Playwright account E2E passes | pass |
| Explain verification without misleading loss state | registration/profile/confirmation UI | success routes redirect directly into profile state | pass |

## Findings

| ID | Severity | Status | Evidence | Impact | Required resolution | Retest evidence |
| --- | --- | --- | --- | --- | --- | --- |
| R-001 | P1 | resolved | `accounts/views.py`; `Account.tsx` | Requests were grouped by type | Unified ordered/paginated API | API test pass; browser E2E pending |
| R-002 | P1 | resolved | `Account.tsx` unified badge | Mismatched status semantics/style | One badge with raw status/display label | build pass; browser E2E pending |
| R-003 | P1 | resolved | `settings.py`, `tasks.py`, `.env.example` | Link could target Django host | `FRONTEND_BASE_URL` | backend check pass; delivered-link E2E pending |
| R-004 | P1 | resolved | `Register.tsx`, `EmailVerificationConfirm.tsx` | Rejected intermediary pages | Profile-only flow | build pass; browser E2E pending |
| R-005 | P1 | resolved | `reports/evidence/unified-guest-request-linking/claimed-request-account.png`; `.gitignore` | Durable feature evidence exists; generated output is ignored | Attach artifact when PR exists | Playwright pass |
| R-006 | P2 | open | Vite/proxy/recommender/assistant files outside approved product scope | Feature and runtime risk coupled in one change | Separate task/plan or explicit plan approval | User decision pending |
| R-007 | P2 | resolved | `accounts/adapters.py`; `accounts/test_guest_claiming.py` | Any social provider email was treated as verified | Claim only an explicitly verified provider email | 29 focused Django tests |
| R-008 | P2 | resolved | `account-request-evidence.spec.ts`; fresh Playwright context | Embedded tabs share state | Isolated guest API flow and fresh account browser | Screenshot `claimed-request-account.png` + pass |

### Resolved review work

- The API now merges the three request types, globally sorts by `created_at`
  descending and paginates that one timeline.
- Every request card uses one pill style and semantic state colour. The
  backend supplies the raw state plus grammatically correct Russian label.
- Verification links use `FRONTEND_BASE_URL`; registration and successful
  confirmation go directly into the profile flow after refreshing profile and
  request/booking query state.
- The account screenshot is kept under `reports/evidence`; transient
  Playwright output is excluded from Git.

### P2 — expanded runtime scope is not isolated from this feature

Vite proxy/default URL changes, assistant/recommender routing, recommender
dependency and local-stack documents were changed to make E2E runnable. They
are not in the approved guest-linking product scope and need either a linked
runtime task/plan and dedicated review, or separation from this branch.

### P2 — remaining automated-coverage limits

The fresh Playwright account uses a guest request created through the real
unauthenticated HTTP endpoint, then verifies its rendered result after an
isolated browser login. The three public form UIs were checked separately in
the local UI run; an all-in-one visual browser script for guest form,
registration and confirmation-link delivery is still a useful future hardening
test, but is not an acceptance blocker.

## User review checklist

- Review the persistent account screenshot before merge.

## Merge/deploy decision

Blocked only by R-006 scope separation and user review. The plan is approved;
do not merge or deploy until both are resolved.

## Follow-ups

- Split or separately approve E2E runtime configuration changes.
- Attach the existing account PNG artifact to a PR when one is created.
