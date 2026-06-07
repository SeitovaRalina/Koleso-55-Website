# Next Steps

Recommended implementation order.

Current priority: bring frontend to production-ready product first. Online payments and deployment come after frontend foundation is solid.

## Phase 1: Frontend UI Kit And Design Tokens

Goal: create custom design system before redesigning production pages.

Tasks:

1. Add Tailwind tokens from `docs/FRONTEND_DESIGN_SYSTEM.md`.
2. Create public `/ui-kit` route.
3. Build custom reusable components:
   - Button;
   - Badge;
   - Input;
   - Select;
   - Checkbox;
   - Tabs;
   - Alert;
   - Skeleton;
   - EmptyState;
   - ErrorState;
   - ExcursionCard;
   - BookingPanel.
4. Add UI kit examples for:
   - colors;
   - typography;
   - buttons;
   - badges;
   - forms;
   - cards;
   - booking states;
   - legal consent checkboxes.
5. Verify desktop and mobile layout.

Why first: homepage and booking page need stable components, tokens, states, and responsive rules.

## Phase 2: Production Homepage

Goal: redesign homepage as premium editorial travel page with real product entry points.

Tasks:

1. Use `hero-bg.jpg` and design-system colors.
2. Keep first screen useful: search/catalog entry, not only marketing copy.
3. Add/upgrade sections:
   - hero;
   - weekly events;
   - editorial destination/story block;
   - popular excursions;
   - how booking works;
   - reviews;
   - certificates teaser;
   - custom request;
   - blog/weekly summary teaser.
4. Add loading/error/empty states where API-driven.
5. Verify mobile and desktop with browser screenshots.

## Phase 3: Production Booking And Order Flow

Goal: guest-first booking page that respects current business rules, even before YooKassa implementation.

Tasks:

1. Make booking available without auth.
2. Keep optional auth benefits visible but not blocking.
3. Show backend fields:
   - excursion;
   - slot;
   - participants;
   - contact data;
   - preferred contact method;
   - comment.
4. Add legal consent checkboxes for guest booking.
5. Show payment placeholder:
   - YooKassa will be main method later;
   - manager fallback exists now;
   - slot is occupied only after payment later.
6. Show negotiated/custom price fallback when price is not fixed.
7. Add order success state:
   - order created;
   - next step: online payment later or manager fallback now;
   - guest order link concept when backend supports it.

## Phase 4: Legal Pages And Registration Consent

Goal: publish legal documents and collect required consent.

Tasks:

1. Add legal pages:
   - `/legal/personal-data-consent`;
   - `/legal/personal-data-policy`.
2. Link original DOCX files from `frontend/public/documents/`.
3. Add footer links.
4. Add required checkboxes to registration.
5. Add required checkboxes to guest booking.

## Phase 5: Frontend Backend Contract Fixes

Goal: make frontend show all existing backend data correctly.

Tasks:

1. Fix recommender API wrappers:
   - unwrap `data.recommendations`;
   - unwrap `data.similar_excursions`;
   - use correct query params.
2. Audit frontend types against backend serializers.
3. Add missing states:
   - loading;
   - error;
   - empty;
   - auth-required;
   - submitting.
4. Make account pages production-ready enough:
   - profile;
   - orders;
   - wishlist;
   - recommendations.

## Phase 6: Secondary Frontend Pages

Goal: add product pages requested by stakeholder after MVP pages.

Tasks:

1. QA/FAQ page.
2. Gift certificate order page.
3. Recommendation system explanation page.
4. About page.
5. Blog page for weekly updates.

## Phase 7: Backend Pricing Foundation

Goal: make `main_service` capable of fixed, adult/child, negotiated, and custom-request prices.

Tasks:

1. Extend excursion pricing model.
2. Add admin fields for:
   - price type: fixed per person, adult/child, negotiated, custom request;
   - adult price;
   - child price;
   - pricing note.
3. Update serializers/API response.
4. Update booking serializer to accept participant breakdown when needed.
5. Add tests for amount calculation.

Why before payments: YooKassa amount must be computed by backend, not frontend.

## Phase 8: Payment App

Goal: YooKassa test payment after booking.

Tasks:

1. Add `payments` Django app.
2. Add `Payment` and `PaymentEvent` models.
3. Add create-payment endpoint.
4. Add status endpoint.
5. Add YooKassa webhook endpoint.
6. Add idempotency and duplicate-webhook tests.
7. Update `.env.example`.

Rules:

- 100% prepayment.
- Slot occupied only after successful payment.
- Negotiated/custom price orders use offline manager fallback.

## Phase 9: Deploy Prep

Goal: one Timeweb service/VPS with frontend + backend.

Tasks:

1. Choose domain.
2. Configure DNS.
3. Choose HTTPS method.
4. Set production env values.
5. Build frontend into nginx.
6. Run compose with proxy profile.
7. Test health, API, payment return, webhook URL.
