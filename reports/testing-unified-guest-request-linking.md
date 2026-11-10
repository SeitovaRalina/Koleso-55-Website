# Testing: unified guest request linking

- Status: passed
- Date: 2026-11-09
- Slug: unified-guest-request-linking
- Plan: reports/plan-unified-guest-request-linking.md
- Implementation: reports/implementation-unified-guest-request-linking.md
- Environment: local Docker Compose + Vite (`127.0.0.1:4173`)

## Test matrix

| Acceptance criterion | Method / command | Result | Evidence |
| --- | --- | --- | --- |
| Authenticated custom-tour submission appears in `Мои заявки` | UI: submit custom tour, open account requests | pass | Card has type, `Новый`, summary and date |
| Authenticated excursion question appears in `Мои заявки` | UI: `/excursion/7`, submit question, open account requests | pass | Linked question card, status `Новое`, summary and timestamp |
| Authenticated certificate request appears in `Мои заявки` | UI: `/certificates`, submit form, open account requests | pass | Certificate card, `Новая`, recipient/amount/format summary |
| Unified list contains all three request types | Browser E2E account screen | pass | Question, custom tour and certificate each visible |
| Question card links to excursion | Browser E2E account screen | pass | `/excursion/7` link present |
| Guest request → verified-email claim | Django integration test | pass | Transactional claim of all four record types; repeat call claims zero additional records |
| Guest request → verified-email claim | Isolated HTTP + Playwright E2E | pass | Guest POST without auth → register → confirmation → fresh Playwright login → visible `Экскурсия на заказ` card |
| Registration and confirmation UX | Code review + TypeScript checks | pass | Successful registration redirects directly to profile; successful confirmation redirects to profile notification, with no success/claim page |
| Unified ordering and account isolation | Django API test | pass | Three types return newest first; another user's record is excluded |
| Social-login identity rule | Django code review | pass | Only provider email explicitly marked verified can trigger historic-record claiming |
| Authenticated contact prefill | Fresh Playwright profile | pass | Question, booking, custom-tour and certificate forms contain profile ФИО, phone and email; guest-only hint is absent |

## Automated checks

- `npm run lint` — pass.
- `docker compose exec -T main_service python manage.py test accounts bookings excursions --keepdb` — pass, 51 tests.
- `docker compose exec -T main_service python manage.py check` — pass.
- `npm run lint` — pass.
- `npx tsc --noEmit --incremental false -p tsconfig.app.json` and `tsconfig.node.json` — pass.
- `npx vite build` — pass. Vite reports existing JS chunk warning over 500 kB.
- Local E2E fixture plus `npx playwright test tests/account-request-evidence.spec.ts tests/authenticated-form-prefill.spec.ts` — pass, 4 cases.

## E2E scenarios

- Login, question submission, certificate submission, custom-tour submission
  and unified personal list verified through real local UI/API.
- Local test tours use real slots and images; detail page displayed full
  interval `27.12 18:30 – 27.12 20:30`.

## Visual check relevant to this feature

- The fresh account screenshot shows an actual claimed custom-tour request in
  `Мои заявки`: type, summary, date and shared `Новая` status pill.
- Persistent artifact:
  `reports/evidence/unified-guest-request-linking/claimed-request-account.png`.

## Not run and why

- PR screenshot upload and merge: no PR/merge requested; no persistent image
  artifacts uploaded because no PR exists. The two local PNG artifacts above
  are ready to attach.

## Defects and residual risk

- Production build initially failed inside the sandbox because its process
  could not launch esbuild; the identical build outside the sandbox passed.
- The full Django suite reaches the unrelated `reviews` toxicity-model test,
  which waits on a third-party ML model download in the local environment.
  The complete changed-backend scope (`accounts`, `bookings`, `excursions`)
  passes 51 tests; this limitation must not be reported as a product pass for
  the unrelated review model.

## Handoff to review

Implementation is ready for final review, then user review before
merge/deploy.
