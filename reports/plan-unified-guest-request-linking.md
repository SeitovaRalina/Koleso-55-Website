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
| 2026-11-08 | Approved plan corrected against rebased source | Existing custom-tour and question flows are preserved; only their ownership/listing behaviour changes |
| 2026-11-08 | Draft updated | User rejected registration and verification intermediary screens; profile-centred verification UX replaces them |
| 2026-11-09 | Draft updated | User required one visual and semantic status system for all request types; review found list ordering does not meet approved newest-first rule |
| 2026-11-09 | Approved | User approved profile-centred verification UX, unified newest-first request timeline and one status system |
| 2026-11-09 | Approved | User approved profile-contact prefill for authenticated custom-tour and certificate forms |
| 2026-11-09 | Approved | User removed SMS-verification implementation detail from all customer-facing copy |
| 2026-11-09 | Approved | User approved hiding guest-linking email hints in custom-tour and certificate forms for authenticated users |

## Goal

Show a customer's requests in `Мои заявки` consistently, including requests
created as a guest before the customer authenticates.

## Current state and evidence

- Guest `TourOrder` records are linked by `accounts.utils.link_guest_bookings`
  when email or phone matches a registered user.
- `CustomTourRequest` is already persisted and attached when the sender is
  authenticated, but guest submissions cannot later be claimed.
- Gift certificate requests have no account relation or personal list.
- The excursion-level `Остались вопросы?` form already persists an
  `ExcursionInquiry` and has an authenticated personal list. Preserve this UI
  and bring it under the same safe claiming policy.
- Current `link_guest_bookings` claims unowned orders on registration by either
  matching email or phone; it does not require `is_email_verified`. A phone is
  not independently verified. Profile phone changes rerun linking; ordinary
  password login currently does not.

## In scope

- One account-linking policy for guest questions about an excursion, custom
  tour requests and gift certificate requests.
- Preserve the existing excursion-level “Остались вопросы?” form and its
  persisted request.
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

## Approved contact prefill

- For authenticated users, custom-tour form pre-fills name, phone and email
  from profile; certificate form pre-fills buyer name, phone and email.
- Prefilled fields stay editable for a particular request and do not update the
  profile when submitted.

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
| Registration success | immediate redirect to profile, no success screen | send verification email; show profile warning that account works now but guest history waits |
| Email unverified in profile | persistent compact warning with exact masked/known email and “Отправить письмо ещё раз” | call existing verification endpoint; show 60-second cooldown and delivery/error state |
| Empty `Мои бронирования` / `Мои заявки`, email unverified | explanatory empty state, not “nothing exists” | link/button to profile verification block |
| Confirmation link succeeds | redirect to profile with a short success notification | invalidate profile/orders/requests queries; profile then shows the updated tabs without an intermediary screen |
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
  `user=request.user`. The list endpoint returns a unified, paginated timeline
  of question/custom-tour/certificate records with `type`, `status`,
  `status_display`, `created_at` and a safe type-specific summary; it orders
  globally by `created_at` descending.
- Email verification links use an explicit public frontend base URL rather
  than a proxied Django request host. Add the non-secret environment example
  and preserve an explicit safe local default for development.
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

## Pending approval: profile-centred verification UX revision

- Registration must redirect directly to `Личный кабинет`, not an “Аккаунт создан” screen.
- The profile keeps a persistent compact warning: “Письмо для подтверждения отправлено на <email>”.
  It includes “Отправить ещё раз”, with delivery/error state and 60-second cooldown.
- Successful confirmation redirects to the profile and shows a brief success notification;
  it does not render an “Email подтверждён” screen or claim-count page.
- Existing unverified empty-state hints remain links to the profile verification block.

## Pending approval: unified request status presentation

- Every card in `Мои заявки` uses one `RequestStatusBadge` component: the
  same pill shape, spacing, font size and semantic colour for equivalent
  states, regardless of request type.
- Semantic palette: `new` blue, `in_progress` amber, `completed` green and
  `cancelled` red. Russian text remains grammatically correct for the request
  type (`Новое` for a question, `Новая` for a certificate/tour).
- API data for a question includes its machine-readable `status` as well as
  the Russian display text. The frontend must not infer a state from a label.
- `Мои заявки` is one combined, newest-first timeline. Pagination must not
  silently omit old records or regroup them by type.

## Approval record

Original linking scope approved by the user in Codex chat on 2026-11-08.
Profile-centred verification UX and unified request rendering were explicitly
approved by the user in Codex chat on 2026-11-09.
