# Business rules map

- Last verified: 2026-11-08
- Evidence: approved product decisions, models/routes
- Owner: project owner; agent updates only after explicit decision

## Booking, account and orders

- Catalogue is built around excursions and dated slots.
- Accounts use unique email; phone is optional at account level.
- Orders record a preferred contact method and at least one contact field.
- Orders have new, confirmed, paid, cancelled and completed states.
- Reviews are moderated; wishlist belongs to authenticated users.

Booking is intended for guests and authorised users. Authorisation provides
saved profile/contact data, order history, wishlist, reviews and personalised
recommendations. Guest flows collect contact and legal-consent data.

## Pricing, payment and cancellation

- Price calculation is backend-owned.
- Default is per person; adult/child and negotiated/custom price models remain
  supported product directions, not assumed current model fields.
- YooKassa remains test-mode only until a separate live-mode decision.
- Prepayment is 100%; slot becomes occupied only after trusted backend payment
  confirmation, never browser return.
- Negotiated/custom price uses manager contact rather than fixed payment.
- Account cancellation is allowed more than 48 hours before start; later cases
  use a refund request. Company cancellation requires full prepayment refund.

## Legal and content

Legal consent and policy documents are published from `frontend/public/documents/`.
Registration and guest booking require the appropriate consents. Legal-version
storage is an open implementation question.

## Current known gap

Current router still protects booking despite guest-booking product rule. This
needs an approved code task.

Do not infer additional request/certificate/account rules from legacy UI. Put
new/changed product behaviour through an approved plan.
