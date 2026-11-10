# Review: unified guest request linking

- Status: approved_for_merge
- Date: 2026-11-09
- Slug: unified-guest-request-linking
- Plan: reports/plan-unified-guest-request-linking.md
- Implementation: reports/implementation-unified-guest-request-linking.md
- Testing: reports/testing-unified-guest-request-linking.md
- PR: https://github.com/SeitovaRalina/Koleso-55-Website/pull/19

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
| R-006 | P2 | resolved | Vite/proxy/recommender/assistant files outside the original guest-linking product scope | Feature and runtime risk coupled in one change | Explicit user approval for a universal local environment; service health and recommender async import verified | Django, recommender and assistant health endpoints return 200; async dependencies import |
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

### P2 — remaining automated-coverage limits

The fresh Playwright account uses a guest request created through the real
unauthenticated HTTP endpoint, then verifies its rendered result after an
isolated browser login. The three public form UIs were checked separately in
the local UI run; an all-in-one visual browser script for guest form,
registration and confirmation-link delivery is still a useful future hardening
test, but is not an acceptance blocker.

## Merge/deploy decision

All review findings are resolved. The user has requested merge and deploy after
this final review. The release must still pass the documented production
preflight, backup, migration and smoke checks.

## Follow-ups

- Attach the existing account PNG artifact to PR №19 if visual evidence is
  refreshed for the release.
