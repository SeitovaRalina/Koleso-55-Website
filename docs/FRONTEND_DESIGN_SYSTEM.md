# Frontend Design System

Цель: единая дизайн-система и UI kit для React frontend "Колесо путешествий 55".

Вдохновение:

- https://travelsnob.ru/ - премиальный travel editorial, крупная фотография, спокойная сетка.
- https://www.manawa.com/en - marketplace excursions, понятный каталог, фильтры, карточки активностей.
- `frontend/public/hero-bg.jpg` - основной источник палитры.

## Характер

- Современный premium editorial travel site with marketplace booking flow.
- Чистый, уверенный, не перегруженный.
- Фото и контент впереди декоративных эффектов.
- Омск/Россия должны ощущаться через реальные изображения, маршруты, места, категории.

## Палитра

Из `hero-bg.jpg`:

| Token | Hex | Use |
| --- | --- | --- |
| `brand.sky` | `#0B8ED8` | primary buttons, active filters, links |
| `brand.deep` | `#0A3F9A` | header accents, hover, hero overlay |
| `brand.mist` | `#D9EEF7` | light sections, selected soft backgrounds |
| `nature.green` | `#6FA36B` | availability, eco/outdoor tags, success |
| `heritage.cream` | `#F4EFE6` | warm page bands, certificate blocks |
| `heritage.brick` | `#9B4A31` | limited accent, historical/cultural tags |
| `neutral.ink` | `#172033` | headings and high-emphasis text |
| `neutral.text` | `#4B5563` | body text |
| `neutral.line` | `#E5E7EB` | borders |
| `neutral.surface` | `#FFFFFF` | cards and panels |

Rule: blue is brand anchor, not whole UI. Use green/cream/brick to avoid one-note palette.

## Typography

- Headings: strong, compact, no negative letter spacing.
- Body: readable, normal tracking.
- Cards and tool panels use smaller headings than hero.
- Russian labels must fit mobile widths.

Recommended scale:

- Page title: 40-56 desktop, 30-36 mobile.
- Section title: 28-36 desktop, 24-28 mobile.
- Card title: 16-20.
- Body: 15-16.
- Meta: 13-14.

## Layout

- Max content width: `1180px`.
- Section spacing: 72-96 desktop, 40-56 mobile.
- Grid gap: 20-28.
- Card radius: 8px.
- Inputs/buttons height: 44-48.
- Excursion image ratio: `3 / 4`.

## Components

Must exist as reusable patterns:

- Button: primary, secondary, ghost, danger, icon.
- Badge: category, status, availability.
- ExcursionCard: image, category, favorite, price, rating, duration.
- FilterSidebar: category, price, duration, location, date.
- BookingPanel: slot, participants, summary, pay action.
- StatusAlert: backend warnings and payment state.
- EmptyState, ErrorState, Skeleton.
- Tabs for account.

## Page Rules

UI Kit:

- Create a dedicated UI kit page.
- Public route: `/ui-kit`.
- UI kit must show colors, typography, buttons, badges, cards, forms, alerts, tabs, skeletons, booking panel states.
- UI kit should use custom Tailwind components, not shadcn/ui.

Homepage:

- Hero may use `hero-bg.jpg`, but text/search must be legible.
- Show real next section above fold where possible.
- Include weekly events, how it works, reviews, certificates, custom request.
- Style direction: closer to premium editorial `travelsnob.ru`.

Catalog:

- Task-first. No giant hero.
- Filters visible desktop, drawer mobile.
- URL params sync.
- Count and sorting visible.

Excursion detail:

- Photos, title, price, rating, duration, category, slots, booking panel.
- Similar excursions from recommender.
- Track analytics view source.

Booking:

- Show all backend fields.
- Show business rules: guest booking, optional auth, slot availability, full prepayment, YooKassa as main payment, manager fallback.
- Slot is occupied only after payment.
- Show adult/child price breakdown when backend supports it.
- Show negotiated/custom price fallback when price is not fixed.
- Never calculate trusted payment amount on frontend; show backend-computed amount.
- YooKassa test mode should be clear in dev/staging.
- Guest booking must include legal consent checkboxes.
- Authorized booking can show compact legal notice if consent already accepted.

Account:

- Tabs: profile, orders, favorites, recommendations.
- Cancel paid order only if event starts in more than 48 hours.
- Otherwise show refund request instructions.

Legal:

- Footer links to personal data consent and policy.
- Registration has required consent checkboxes.
- Guest booking has required consent checkboxes.
- Legal document pages:
  - `/legal/personal-data-consent`
  - `/legal/personal-data-policy`
- Original DOCX files live in `frontend/public/documents/` and should be linked for download.

## Accessibility

- All controls keyboard reachable.
- Form labels visible or properly associated.
- Color not sole indicator.
- Focus ring visible.
- Images have meaningful alt.

## Implementation Notes

Start by extending Tailwind tokens in `frontend/tailwind.config.js`, then migrate components gradually.

Avoid:

- raw hex colors inside components after tokens exist;
- nested cards;
- decorative blobs;
- huge marketing sections on operational pages;
- hiding backend errors behind generic text.
