# Plan: unified guest request linking

- Status: draft
- Date: 2026-11-08
- Slug: unified-guest-request-linking
- Owner: user and agent
- Approval: awaiting

## Goal

Show a customer's requests in `Мои заявки` consistently, including requests
created as a guest before the customer authenticates.

## Current state and evidence

- Guest `TourOrder` records are linked by `accounts.utils.link_guest_bookings`
  when email or phone matches a registered user.
- `CustomTourRequest` is attached only when the sender is already
  authenticated.
- Gift certificate requests have no account relation or personal list.
- A prior question-form flow existed for an excursion, but the current
  `Остались вопросы?` block is only a contacts link. Restoring that flow is
  separately in scope only after this plan is approved.

## In scope

- One account-linking policy for guest questions about an excursion, custom
  tour requests and gift certificate requests.
- Display those owned records in `Мои заявки` after successful linking.
- Preserve existing `TourOrder` linking while making its safety rules explicit.
- The three request types and their planned statuses:
  - question: `Новый` → `В работе` → `Вопрос решён` / `Отменён`;
  - custom tour: `Новая` → `В работе` → `Обработана` / `Отменена`;
  - certificate: `Новая` → `В работе` → `Оформлена` / `Отменена`.

## Out of scope

- Website chat or manager-to-customer messages.
- Payment, certificate issuance, SMS infrastructure or a new identity system.
- Automatically claiming records that are already owned by another account.

## Proposed UX and business rules

- Keep the tab name `Мои заявки`.
- List questions, custom tours and certificates newest first, each with a type,
  human-readable status and safe summary. Booking remains in `Мои бронирования`.
- Managers contact customers outside the site and update only the appropriate
  processing status in Django Admin.
- A question card links to its excursion; the other two cards are status
  trackers, not a chat or detail page.

## Data model, API, Admin, migrations

- Add optional `user` relations and migration(s) where absent.
- Expose authenticated list endpoints that filter only by `user=request.user`.
- Attach records immediately when an authenticated user submits a form.
- Add a transactional service that claims only currently unowned guest records
  matching an approved identity rule; call it on registration, login and
  profile-contact changes.
- Django Admin keeps original submitted data read-only and lets managers change
  only processing status.

## Acceptance criteria

- An authenticated sender sees a newly sent request in `Мои заявки`.
- A matching unowned guest request appears after the approved linking event.
- A non-matching account and a second account cannot view or claim it.
- Manager status changes appear with Russian labels in the account.
- Guest requests remain visible in Admin regardless of account linkage.

## Verification plan

- Django unit/API tests for authenticated creation, guest creation, matching,
  non-matching and already-owned records for every request type.
- Admin permission and editable-field tests.
- Frontend lint/build.
- Local E2E: guest submit → approved identity event → `Мои заявки`; authenticated
  submit → immediate list; desktop and mobile screenshots in the PR.

## Risks and rollback

- Contact matching can expose a guest record to a person who does not own that
  contact. The exact identity rule is an open decision below.
- Migration adds nullable ownership only; rollback is to stop new linking while
  preserving submitted records.

## Open decisions

1. Identity rule: match only a verified email now, or also match a phone that
   has not been independently verified by SMS?
2. Confirm restoration of the `Остались вопросы?` form as part of this work,
   rather than a separate approved plan.

## Approval record

Awaiting explicit user approval after the open decisions are resolved. No code,
migration, API or UX change may start before then.
