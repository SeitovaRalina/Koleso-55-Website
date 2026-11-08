# Payments

- Status: planned; no live payment implementation is approved
- Owner: main-service domain

YooKassa is intended primary post-booking payment method in test mode. Backend computes amount, owns idempotency and accepts payment state only from trusted webhook/status verification. Browser return is UX only.

Future implementation needs payment record, stable idempotency key, provider payment ID, amount/currency/status and deduplicated provider events. Successful payment changes order/slot transactionally and never double-books seats. Negotiated/custom price uses manager workflow.

Any payment task needs an approved plan plus webhook, cancel, duplicate-event, wrong-amount and unknown-payment tests.
