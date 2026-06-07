# Product Decisions

Source of truth for product and business decisions.

## Booking And Auth

- Booking is available to all users.
- Authorization is optional.
- Authorized user benefits:
  - saved profile/contact data;
  - ability to leave reviews/comments;
  - ability to see own orders;
  - ability to add excursions to wishlist;
  - personalized recommendations.
- Guest booking must collect required contact data and legal consents.
- Guest can receive order access link.

## Payment

- YooKassa is the main payment method.
- YooKassa works only in test mode until explicit decision to switch to live mode.
- Manager contact is fallback, not primary flow.
- Payment is available immediately after booking creation.
- Prepayment is 100%.
- Slot is not reserved before payment.
- Slot becomes occupied only after successful payment confirmation.
- `TourOrder.status = paid` must be set only after trusted YooKassa success webhook/status sync.

## Pricing

- Prices are defined only by backend.
- `main_service` must support multiple pricing models.
- Default price model: price per person.
- Some excursions may have adult and child prices.
- Child age boundary is not fixed yet; backend must store prices without hardcoding age rule in frontend.
- Some excursions may have negotiated/custom price.
- Custom excursions require request flow instead of direct fixed-price payment.
- Negotiated/custom price flow: manager contacts user outside the site.

## Cancellation And Refunds

User can cancel an order from account if cancellation is at least 48 hours before event start.

Customer-facing copy:

> Чтобы отменить экскурсию, зайдите в личный кабинет, выберите нужный заказ, нажмите кнопку «Отменить». Если вы хотите отменить экскурсию уже после даты ее проведения или есть какие-то особые обстоятельства, мешающие вашему присутствию на экскурсии, заполните заявление на возврат. Мы его рассмотрим и ответим вам в течение 10 дней (обычно быстрее).

Rules:

- Before 48h: account cancellation is allowed.
- Less than 48h before event: user must submit refund request/application.
- After event date: user must submit refund request/application.
- If guide/company cancels, prepayment is fully refunded.
- Refund automation is not MVP unless explicitly requested; show instructions and manager fallback.

## Legal Documents

Need two legal documents on site:

- `frontend/public/documents/Согласие_туриста_или_иного_заказчика_ТП_на_обработку_ПД_.docx`
- `frontend/public/documents/Политика_в_отношении_обработки_персональных_данных.docx`

Placement:

- Registration form:
  - required checkbox for personal data processing consent;
  - required checkbox accepting personal data policy.
- Guest booking form:
  - same required checkboxes, because guest provides personal data without account.
- Authorized booking form:
  - show compact consent notice if consents already accepted on registration;
  - ask again only if legal version changed or if booking collects new recipient/tourist data.
- Footer:
  - permanent links to both documents.
- Dedicated legal pages:
  - `/legal/personal-data-consent`
  - `/legal/personal-data-policy`

Implementation note:

- Original DOCX files are approved for public site display.
- Convert DOCX to web-readable HTML/Markdown/PDF for site display, and keep DOCX download links.
- Track legal document version and accepted timestamp if backend stores consent history later.

## Frontend Priority

Current implementation priority:

1. Bring frontend to production-ready quality first.
2. Build custom UI kit at dev-only `/ui-kit`.
3. Redesign homepage.
4. Redesign booking/order flow.
5. Add legal pages and consent UI.
6. Fix existing frontend/backend contract gaps.
7. Delay online payments and deploy until frontend foundation is stable.

MVP page priority:

1. Homepage.
2. Booking/order page.
3. UI kit page.

Next priority:

- QA/FAQ page.
- Gift certificate order page.
- Recommendation system explanation page.
- About page.
- Blog page for weekly updates.

## Frontend Style

- Direction: premium editorial, closer to current Koleso design system.
- Use `manawa.com` mainly for catalog usability and activity-card clarity.
- Build custom UI kit; do not adopt shadcn/ui as dependency for now.
- UI kit route is dev-only: `/ui-kit`.
- Use palette from `frontend/public/hero-bg.jpg`.
- Homepage follows the approved reference order: hero info, search, nearest events, how it works, reviews + organization, certificate, contacts, footer.
- Header search appears only on the homepage.
- Hero location options come from `Excursion.LocationType` and submit to catalog as `location_type=city|suburban|russia`.
- Date control is one visual field and submits `date_from` or `date_from` + optional `date_to`.
- Nearest events block shows up to 8 shared catalog cards and uses `nearest_slots` for slot overlay.
- Homepage reviews are selected in Django admin from excursion reviews with `show_on_homepage`.
- Homepage review photo is selected from review images via `is_homepage_main` and `homepage_order`.
- Footer includes VK, Telegram, Max, logo, and brand copy.
- Contact/social/review URLs live in `frontend/src/config/contacts.ts`.

## Deployment

- Domain is not ready yet.
- Deployment planning must include domain purchase/connection, DNS, HTTPS, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and YooKassa return/webhook URLs.
