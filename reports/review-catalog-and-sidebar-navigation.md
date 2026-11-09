# Review: catalog and sidebar navigation

- Status: approved_for_user_review
- Date: 2026-11-09
- Reviewer stance: independent check against approved plan and actual diff
- Plan: `reports/plan-catalog-and-sidebar-navigation.md`
- Implementation: `reports/implementation-catalog-and-sidebar-navigation.md`
- Testing: `reports/testing-catalog-and-sidebar-navigation.md`

## Scope review

Reviewed all changed and untracked task files. Every source/test change maps
to an approved catalogue, side-panel or certificate-copy requirement. No
backend, API, migration, dependency, Header/footer or unapproved UX change was
found.

## Findings

| ID | Severity | Evidence | Resolution |
| --- | --- | --- | --- |
| R-001 | low | User refined the approved copy from a personal name to “Менеджер” during implementation. | Resolved: plan change log, task decision and sidebar text agree. |
| R-002 | low | Local Django API was unavailable, so live catalogue data could not be exercised. | Open operational limitation, not a product-code defect: mocked-browser coverage plus lint/type/build pass; repeat live E2E once the local API is running. |
| R-003 | high | Whole-panel `overflow-y-auto` contradicted the user's intended DNS-like interaction and caused wheel scrolling inside every audited side panel. | Resolved: plan was revised and approved; removed whole-panel scrolling from filters, certificate and booking sidebars. Browser inspection confirms `sticky` + `overflow-y: visible` on all three. |
| R-004 | high | The catalogue-specific affix was a visual expansion beyond the final approved in-layout pattern and risked an unnatural horizontal jump/overlay. | Resolved: removed all affix behaviour. Catalogue filters now use the same `lg:sticky lg:top-24` grid-column treatment as certificate help and booking. |

## Independent checks

- Reviewed pagination set construction: it produces first/last/current
  neighbours and one ellipsis per omitted range; controls are hidden where no
  adjacent page exists.
- Reviewed scrolling guard: only `goToPage` enables it; filter, search and
  sort updates retain existing page-reset behaviour without a forced scroll.
- Reviewed breakpoint classes: sticky behavior is `lg`-only with no
  whole-panel scroll, and four columns are `xl`-only when filters are hidden.
- Re-ran lint, TypeScript, build and focused Playwright checks described in
  the testing report; all passed.
- Reviewed the test fixture correction: its old glob matched `src/api/*`
  source modules as well as HTTP `/api/*` calls. The host-and-path-scoped
  matcher restores a valid browser test without changing production code.

## Merge decision

No unresolved code finding blocks user review. Do not merge or deploy until
the user accepts this review; separately repeat live E2E when local backend is
available if that operational confidence is required.
