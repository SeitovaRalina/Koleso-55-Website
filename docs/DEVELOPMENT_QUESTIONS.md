# Development Questions

Current answered decisions live in `docs/PRODUCT_DECISIONS.md`.

## Answered

- Booking is available to everyone.
- Authorization is optional and mainly gives saved user data, reviews/comments, order history, wishlist, recommendations.
- YooKassa is main payment method; manager contact is fallback.
- YooKassa only test mode for now.
- Payment happens immediately after booking.
- Prepayment is 100%.
- Slot is occupied only after successful payment, not before.
- Price is usually per person.
- Some excursions need adult/child prices.
- Some excursions need negotiated/custom price.
- Prices are backend-owned; `main_service` must support multiple pricing models.
- Negotiated/custom price flow uses offline manager contact.
- Guest can receive order access link.
- Paid order can be cancelled from account only at least 48 hours before event.
- Late cancellation or special circumstances require refund request/application.
- If guide/company cancels, prepayment is fully refunded.
- Fiscalization/receipts are not needed now.
- Legal docs must be shown as required consents in registration and guest booking.
- Legal DOCX files are in `frontend/public/documents/`.
- Frontend MVP: homepage and booking/order page.
- Later pages: QA/FAQ, certificates, recommendation info, about, blog.
- Visual direction: closer to premium editorial `travelsnob.ru`.
- UI kit page is needed.
- UI kit route is public: `/ui-kit`.
- Build custom UI kit, no shadcn/ui for now.
- Domain is not ready.

## Open Product Questions

1. Which excursion types must exist in MVP: group, individual, corporate, custom, gift certificate?
2. For adult/child prices: what age counts as child?
3. Which order statuses should be visible to guest user after booking without account?
4. Should guest receive order access link by email, SMS, or both?
5. Should reviews require moderation before publication?
6. Should recommendations work for anonymous session users or only authorized users?
7. Should the site explain why an excursion is recommended?

## Open Legal Questions

1. Should legal docs be converted to HTML pages, downloadable DOCX/PDF, or both?
2. Should backend store consent version and timestamp?
3. Does booking collect data for multiple tourists or only one customer/contact person?

## Open Payment Questions

1. Should failed/canceled YooKassa payment keep order `new`, or set a separate payment status while order stays unpaid?
2. Should payment amount support child/adult participant breakdown in MVP?
3. Should manager be able to create payment link manually from admin later, or keep offline contact only?
4. Should refund request be a site form or a downloadable document?

## Open Frontend Questions

1. Which real photos can be used besides `hero-bg.jpg`, `certificate.jpg`, `logo.png`?
2. Should homepage use large editorial story sections, or stay shorter with strong booking entry?
3. Should blog be managed by backend admin, static markdown, or placeholder until backend exists?

## Open Deploy Questions

1. Which domain will be used?
2. Will HTTPS be configured by Timeweb panel, certbot on VPS, or external CDN/proxy?
3. Need staging environment before production?
4. Where should media files live: VPS volume or object storage?
5. What PostgreSQL backup schedule is acceptable?
