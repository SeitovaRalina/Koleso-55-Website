# YooKassa Implementation

Цель: онлайн-оплата заказа экскурсии через YooKassa в Django `main_service`.

Текущее решение: использовать только YooKassa test mode, пока владелец продукта явно не разрешит live mode.

Источники:

- YooKassa API reference: https://yookassa.ru/developers/api
- YooKassa interaction format and idempotency: https://yookassa.ru/developers/using-api/interaction-format
- YooKassa webhooks: https://yookassa.ru/developers/using-api/webhooks
- YooKassa payment process: https://yookassa.ru/developers/payment-acceptance/getting-started/payment-process
- Python SDK: https://pypi.org/project/yookassa/

## Решения

- Payment ownership: Django `main_service`.
- Recommender не участвует в оплате.
- YooKassa is the primary payment method after booking.
- Manager contact is fallback when online payment is unavailable or price is negotiated.
- Payment mode: test only.
- Prepayment is 100%.
- Slot is not reserved before payment.
- Slot becomes occupied only after successful payment.
- Payment amount is computed by backend only.
- `main_service` must support fixed per-person, adult/child, negotiated, and custom-request pricing before final payment implementation.
- Frontend получает `confirmation_url` и редиректит пользователя в YooKassa.
- Business state меняется только на backend.
- `TourOrder.status = paid` выставляется после webhook `payment.succeeded` или после server-side status sync.
- Frontend return URL нужен только для UX, не для trusted confirmation.

## Env vars

```env
YOOKASSA_SHOP_ID=change-me
YOOKASSA_SECRET_KEY=change-me
YOOKASSA_RETURN_URL=https://example.com/payment/return
YOOKASSA_WEBHOOK_SECRET=change-me
YOOKASSA_CAPTURE=true
YOOKASSA_VAT_CODE=1
YOOKASSA_CURRENCY=RUB
```

Для test mode:

- использовать test shop credentials;
- показывать в dev/staging UI, что платеж тестовый;
- не подключать live secret key;
- webhook URL все равно должен быть доступен извне, если тестируется полный webhook flow.

Для production позже:

- secrets хранить в Timeweb env/секретах, не в git.
- test credentials не смешивать с live.
- webhook URL должен быть HTTPS.

## Модель данных

Добавить `Payment`:

```python
class PaymentStatus(models.TextChoices):
    PENDING = "pending"
    WAITING_FOR_CAPTURE = "waiting_for_capture"
    SUCCEEDED = "succeeded"
    CANCELED = "canceled"
    FAILED = "failed"

class Payment(models.Model):
    order = models.ForeignKey("bookings.TourOrder", on_delete=models.PROTECT, related_name="payments")
    provider = models.CharField(max_length=32, default="yookassa")
    provider_payment_id = models.CharField(max_length=128, unique=True, null=True, blank=True)
    idempotence_key = models.UUIDField(unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="RUB")
    status = models.CharField(max_length=32, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    confirmation_url = models.URLField(blank=True)
    raw_request = models.JSONField(default=dict, blank=True)
    raw_response = models.JSONField(default=dict, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

Опционально добавить `PaymentEvent`:

```python
class PaymentEvent(models.Model):
    provider = models.CharField(max_length=32, default="yookassa")
    event_id = models.CharField(max_length=160, unique=True)
    event_type = models.CharField(max_length=80)
    provider_payment_id = models.CharField(max_length=128, db_index=True)
    payload = models.JSONField()
    received_at = models.DateTimeField(auto_now_add=True)
```

## Create payment flow

1. User creates `TourOrder`.
2. User clicks pay.
3. Backend validates:
   - order belongs to user or guest session policy passes.
   - order status is `new` or `confirmed`.
   - slot still has enough seats.
   - no successful payment already exists.
   - order has fixed backend-computed payable amount; negotiated/custom price orders use manager fallback.
4. Backend creates/reuses local `Payment` with stable `idempotence_key`.
5. Backend calls YooKassa create payment with:
   - amount
   - currency `RUB`
   - confirmation `{ type: "redirect", return_url }`
   - capture setting
   - metadata `{ order_id, payment_id }`
6. Backend stores `provider_payment_id`, status, `confirmation_url`.
7. Frontend redirects to `confirmation_url`.

## Webhook flow

Handle at `POST /api/payments/yookassa/webhook/`.

Accepted events:

- `payment.succeeded`
- `payment.canceled`
- optionally `payment.waiting_for_capture`

Rules:

- Save raw event first with unique `event_id`.
- If duplicate event: return `200`.
- Find local payment by `provider_payment_id`.
- If not found: fetch payment from YooKassa API, log warning, return `200` unless security policy says reject.
- On `succeeded`:
  - lock payment row.
  - lock order row.
  - verify amount and currency.
  - set payment `succeeded` only if not already succeeded.
  - set order `paid` only once.
  - book participants once.
- On `canceled`:
  - set payment `canceled`.
  - keep order unpaid; do not occupy slot.

## Cancellation And Refund Rules

- User can cancel paid order from account only if event starts in more than 48 hours.
- If less than 48 hours remain, user must submit refund request/application.
- If event date has passed, user must submit refund request/application.
- If guide/company cancels, prepayment must be fully refunded.
- Refund automation is not MVP unless requested; MVP can show refund instructions and manager fallback.

## Idempotency

YooKassa uses `Idempotence-Key` for POST requests. Use stable key per local payment, not random per retry.

Recommended key source:

```python
uuid.uuid5(uuid.NAMESPACE_URL, f"koleso55:order:{order.id}:payment:{payment.id}")
```

## Security

- Do not trust frontend redirect.
- Do not expose YooKassa secret to frontend.
- Use HTTPS for webhook and return URL.
- Check payment amount from YooKassa before marking order paid.
- Check metadata order id matches local payment/order.
- Add request logging without secret headers.
- Rate-limit payment create endpoint if exposed to anonymous users.

## Tests

Required tests:

- Create payment for new order.
- Reuse existing pending payment.
- Reject create payment for already paid order.
- Webhook `payment.succeeded` marks order paid.
- Duplicate webhook does not double-book slot.
- Webhook `payment.canceled` updates payment only.
- Webhook with wrong amount does not mark paid.
- Unknown payment id is handled safely.

## Frontend tasks

- Add "Pay" action on order detail.
- `POST /api/payments/orders/{id}/create/`.
- Redirect browser to `confirmation_url`.
- Add return page that calls backend status endpoint and shows current state.
- Do not mark local order paid from query params.
- Show test payment notice in dev/staging.
- For custom/negotiated price orders, show manager fallback instead of YooKassa button.
- For adult/child pricing, frontend sends participant breakdown; backend returns computed amount.
