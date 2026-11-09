# Task: catalogue and sidebar navigation

- Status: implemented; awaiting user review
- Multica: not applicable; user-requested follow-up in PR #19
- Last verified: 2026-11-09
- Evidence: `reports/plan-catalog-and-sidebar-navigation.md`
- Owner: user and agent

## Outcome and non-goals

Improve catalogue density/pagination and audited side-panel behaviour without
changing catalogue filter logic, booking/certificate business rules or backend
contracts.

## Scope and affected areas

- Catalogue grid, pagination and filter-sidebar stickiness.
- Sticky contract of existing booking and certificate side panels.
- Certificate guidance copy and Irina Rusnak contact label.

## Decisions and open questions

- Approved: exact pagination behaviour, sticky rules, certificate copy with
  “Менеджер” in the process, and visible phone attribution ` (Ирина Руснак)`
  after the number.
- Approved revision: remove whole-panel scrolling from catalogue, certificate
  and excursion booking sidebars; retain scrolling only inside an expanded
  long category list.
- Final approved revision: catalogue filters follow the same in-layout sticky
  behaviour as certificate and booking sidebars; no fixed/affix layer and no
  overlay of content or footer.

## Lifecycle links

- Plan: `reports/plan-catalog-and-sidebar-navigation.md`
- Implementation: `reports/implementation-catalog-and-sidebar-navigation.md`
- Testing: `reports/testing-catalog-and-sidebar-navigation.md`
- Review: `reports/review-catalog-and-sidebar-navigation.md`
