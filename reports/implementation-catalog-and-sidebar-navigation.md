# Implementation: catalog and sidebar navigation

- Status: complete
- Date: 2026-11-09
- Plan: `reports/plan-catalog-and-sidebar-navigation.md`
- Task: `harness/tasks/active/catalog-and-sidebar-navigation.md`

## Delivered scope

- Catalogue uses three desktop columns with filters shown and four from `xl`
  when desktop filters are hidden; mobile and `sm` layouts remain one/two
  columns.
- The catalogue filter panel is sticky only from `lg`, stays below Header in
  its normal grid column and naturally stops before the footer. There is no
  JavaScript affix, fixed positioning or whole-panel scrollbar.
- Pagination now has `Предыдущая`/`Следующая`, compact page ranges with
  ellipses, keeps URL filters/search/sorting and scrolls to result controls
  only after an explicit page change.
- Existing booking and certificate side panels use the same desktop in-layout
  sticky contract and remain ordinary document-flow blocks below `lg`.
- Certificate sidebar now has the approved explanatory copy, uses “Менеджер”
  in the process description and keeps the first contact phone actionable as
  `+7 … (Ирина Руснак)`.

## Changed files

- `frontend/src/pages/Catalog.tsx`
- `frontend/src/components/catalog/FilterSidebar.tsx`
- `frontend/src/pages/Certificates.tsx`
- `frontend/src/pages/ExcursionDetail.tsx`
- `frontend/tests/catalog-reset.spec.ts`

## Deliberate non-changes

- No backend, API, migration, filter semantics, booking/certificate
  submission behaviour, Header or footer changes.
- No new contact data or user-facing flow was introduced.

## Plan revisions applied

- After initial approval, the user replaced the personal name in certificate
  process text with “Менеджер”. The plan revision and implementation match it.
- After visual review, the user rejected whole-panel scrolling for filters,
  certificate guidance and excursion booking. Removed `max-height` and
  `overflow-y-auto` from all three panels; only the existing expanded category
  list retains its own scroll.
- The user then rejected the catalogue-specific affix experiment. It was
  removed in favour of the same simple `lg:sticky lg:top-24` treatment used by
  certificate help and excursion booking.
