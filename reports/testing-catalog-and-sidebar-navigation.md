# Testing: catalog and sidebar navigation

- Status: passed with local-runtime limitation
- Date: 2026-11-09
- Plan: `reports/plan-catalog-and-sidebar-navigation.md`
- Implementation: `reports/implementation-catalog-and-sidebar-navigation.md`

## Automated checks

| Check | Result |
| --- | --- |
| `npm run lint` | passed |
| `npx tsc --noEmit --incremental false -p tsconfig.app.json` | passed |
| `npx tsc --noEmit --incremental false -p tsconfig.node.json` | passed |
| `npm run build` | passed; existing Vite chunk-size warning only |
| `npm run test:catalog-reset` | passed, 8 Playwright cases |
| final `npm run build` after sidebar revision | passed; existing Vite chunk-size warning only |

## Browser scenarios covered

- Existing direct-link/reset and mobile filter scenarios remain green.
- At `xl`, hiding filters selects the four-column catalogue class and does not
  create horizontal overflow.
- Pagination test checks Russian control copy, ellipses, query preservation,
  current-page state and return to result controls.
- Certificate panel test checks approved copy/contact, desktop sticky CSS,
  normal mobile position and no horizontal overflow.
- The focused test asserts the in-layout sticky contract for catalogue filters
  (`position: sticky`, `top: 96px`, `overflow-y: visible`) and confirms the
  equivalent certificate behaviour plus normal mobile document flow.
- The test API mock now targets only browser requests to `/api/`; it no longer
  intercepts Vite source modules under `src/api/` and returns JSON as a module.
- Live local verification used 20 temporary, clearly labelled pagination
  records in addition to the existing five. Django returned 25 active records
  as pages of 12, 12 and 1; the browser opened `/catalog?page=2` and
  `/catalog?page=3` and rendered the corresponding records and controls.

## Local data note

The extra records are local Docker/Postgres test data only. They are named
“Локальная проверка пагинации 01” through “20”, include valid slots, are not
part of Git and must not be seeded into production.
