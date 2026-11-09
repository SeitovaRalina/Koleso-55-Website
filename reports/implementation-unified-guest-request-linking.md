# Implementation: unified guest request linking

- Status: complete
- Date: 2026-11-09
- Slug: unified-guest-request-linking
- Plan: reports/plan-unified-guest-request-linking.md

## Delivered scope

- Added verified-email-only, transactional and idempotent claiming for guest
  bookings, excursion questions, custom-tour requests and certificate requests.
- Added nullable ownership for certificate requests and cancelled inquiry status.
- Added authenticated lists for custom-tour and certificate requests; combined
  all three request types in `Мои заявки`.
- Authenticated form submissions attach to the current user immediately.
- Added account email-verification confirmation route and claim result API
  handling.
- Added same-origin Vite proxy defaults for local full-stack testing and fixed
  recommender's missing `greenlet` dependency.
- Replaced type-grouped request rendering with authenticated
  `GET /api/accounts/my-requests/`: globally newest-first, paginated request
  records with a type, raw status and display status.
- Replaced registration/confirmation intermediary UX with profile redirect and
  profile success notice. Successful confirmation refreshes profile state and
  invalidates request/booking queries before redirect; verification emails now
  use `FRONTEND_BASE_URL`.
- Prefill authenticated custom-tour and certificate forms from the editable
  profile data in the Russian ФИО order (surname, name, patronymic), without
  overwriting that profile on submission.
- Keep the guest email-linking hint only for guests; an authenticated user sees
  no registration-oriented copy in those prefilled forms.
- Restricted social-login claiming to provider emails explicitly marked as
  verified; an arbitrary provider `email` value is no longer an identity key.
- Added a permanent browser evidence test and ignored Playwright's generated
  `frontend/test-results/` output.

## Deliberate deviations and open work

- Clean anonymous-browser claiming remains pending because the embedded
  browser shares authentication state across tabs.
- No merge or deploy performed.

## Migrations and compatibility

- `bookings/0007_giftcertificaterequest_user.py`
- `excursions/0011_inquiry_cancelled_status.py`

Both migrations add nullable data and preserve existing submitted records.
