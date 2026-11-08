# Plan: unified guest request linking

- Status: approved
- Date: 2026-11-08
- Slug: unified-guest-request-linking
- Owner: user and agent
- Approval: user explicitly approved verified-email-only linking, ordinary-login reconciliation and verification UX in Codex chat, 2026-11-08

## Revision log

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-08 | Draft created | Unified request/account-linking proposal |
| 2026-11-08 | Draft updated | User confirmed restoration of the former “Остались вопросы?” form in this scope |
| 2026-11-08 | Draft updated | User selected verified-email-only automatic claiming; full verification/linking UX proposed |
| 2026-11-08 | Approved | User approved ordinary-login reconciliation and proposed verification copy/UX |

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
  `Остались вопросы?` block is only a contacts link. User explicitly confirmed
  restoration of that form in this scope.
- Current `link_guest_bookings` claims unowned orders on registration by either
  matching email or phone; it does not require `is_email_verified`. A phone is
  not independently verified. Profile phone changes rerun linking; ordinary
  password login currently does not.

## In scope

- One account-linking policy for guest questions about an excursion, custom
  tour requests and gift certificate requests.
- Restore the excursion-level “Остались вопросы?” form and persist its request.
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
- Automatic claiming uses **only the account's verified email**. Phone is never
  an automatic ownership key until a future independent SMS-verification flow.
  Existing phone-based order linking is replaced for future claims; already
  owned records remain owned.
- An authenticated sender is linked immediately. A guest may submit with a
  phone-only contact method, but sees neutral help text: such a record cannot
  appear automatically in an account until the product adds phone verification.
- The verified-email claim runs transactionally after email confirmation, after
  trusted social login with an email, and at every ordinary password login as
  an idempotent reconciliation. It claims only unowned records and never moves
  a record owned by another account.

### Email-verification UX

Current UI discards backend registration hint and has no verification state.
Replace it with these states:

| Moment | UI | Action/result |
| --- | --- | --- |
| Registration success | success screen before redirect: “Подтвердите email, чтобы увидеть прошлые бронирования и заявки” | send verification email; explain that account works now but guest history waits |
| Email unverified in profile | persistent compact warning with exact masked/known email and “Отправить письмо ещё раз” | call existing verification endpoint; show 60-second cooldown and delivery/error state |
| Empty `Мои бронирования` / `Мои заявки`, email unverified | explanatory empty state, not “nothing exists” | link/button to profile verification block |
| Confirmation link succeeds | confirmation page says email confirmed and gives claimed counts by record type | invalidate profile/orders/requests queries; link to relevant tabs |
| Email verified, no matches | neutral empty state | do not imply records were lost |

Email stays read-only in profile. Guest forms state: “Чтобы позже увидеть
заявку в личном кабинете, укажите email и подтвердите его после регистрации.”
Email remains mandatory only when contact method is Email; phone-only requests
remain valid but are not automatically claimed.

## Data model, API, Admin, migrations

- Add optional `user` relations and migration(s) where absent.
- Expose authenticated list endpoints that filter only by `user=request.user`.
- Attach records immediately when an authenticated user submits a form.
- Replace `link_guest_bookings` with a transactionally safe verified-email
  claim service shared by orders, questions, custom tours and certificates.
  It returns per-type claimed counts; call it after email confirmation, trusted
  social login and ordinary login. Do not call it solely after registration or
  phone/profile change.
- Extend email-confirmation response with claim summary. Add authenticated
  requests-list API and request serializers/types; all list queries scope to
  `user=request.user`.
- Django Admin keeps original submitted data read-only and lets managers change
  only processing status.

## Acceptance criteria

- An authenticated sender sees a newly sent request in `Мои заявки`.
- A matching unowned guest request appears after the approved linking event.
- A non-matching account and a second account cannot view or claim it.
- Manager status changes appear with Russian labels in the account.
- Guest requests remain visible in Admin regardless of account linkage.
- Unverified registration and phone-only guest contact cannot claim historic
  records; UI explains exact next step without claiming records are absent.
- A repeat login/confirmation never duplicates or reassigns a record.

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

1. Confirm proposed ordinary-login reconciliation: verified-email-only,
   idempotent claim of currently unowned records.
2. Confirm exact user-facing copy/tone for verification messages, or delegate
   final copy to implementation within this meaning.

## Approval record

Awaiting explicit user approval after the open decisions are resolved. No code,
migration, API or UX change may start before then.
