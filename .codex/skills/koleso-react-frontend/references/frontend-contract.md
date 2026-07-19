# Frontend Contract Reference

Use this file when implementing frontend API integration.

## Same-Origin Deploy

Target deployment: one Timeweb service/VPS running frontend + backend behind nginx.

Frontend env:

```env
VITE_API_URL=/api
VITE_RECOMMENDER_URL=/api/v1
```

Local dev env:

```env
VITE_API_URL=http://localhost:8001/api
VITE_RECOMMENDER_URL=http://localhost:8002/api/v1
```

## Recommender Response Shape

Do not return raw `response.data` from recommender API wrappers unless page expects object.

```ts
const response = await axios.get(`${RECOMMENDER_URL}/recommendations/user/${userId}`)
return response.data.recommendations
```

```ts
const response = await axios.get(`${RECOMMENDER_URL}/similar/${excursionId}`)
return response.data.similar_excursions
```

## Booking And Payment UX

Booking is public. Auth is optional.

Order status labels:

- `new` -> "Новый"
- `confirmed` -> "Подтвержден"
- `paid` -> "Оплачен"
- `cancelled` -> "Отменен"
- `completed` -> "Выполнен"

Cancellation visible only for `new` and `confirmed`.

For paid orders, cancellation from account is allowed only if event starts in more than 48 hours. Otherwise show refund request instructions.

YooKassa is test mode only until product owner explicitly switches to live.

YooKassa is main payment path after booking. Manager contact is fallback.

Slot is occupied only after successful payment.

Payment amount is backend-owned. Frontend sends participant choices and displays backend-computed amount.

Negotiated/custom price orders use offline manager contact, not YooKassa button.

Legal DOCX files:

- `/documents/Согласие_туриста_или_иного_заказчика_ТП_на_обработку_ПД_.docx`
- `/documents/Политика_в_отношении_обработки_персональных_данных.docx`
