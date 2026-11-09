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

## Runtime limitation

The local Django API at `127.0.0.1:8088` was unavailable during this pass.
Catalogue Playwright scenarios therefore use deterministic intercepted API
responses; they validate frontend interaction and layout but not live backend
data. This task does not alter backend contracts.
