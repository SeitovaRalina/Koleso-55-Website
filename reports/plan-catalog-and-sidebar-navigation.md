# Plan: catalog and sidebar navigation

- Status: approved
- Date: 2026-11-09
- Slug: catalog-and-sidebar-navigation
- Owner: user and agent
- Branch: `fix/slots-about-footer`
- Approval: user approved in Codex chat on 2026-11-09; phone attribution
  corrected to appear directly after the number.

## Goal

Make the catalogue easier to scan and navigate, keep relevant desktop side
panels visible below the fixed header, and turn the certificate sidebar into
useful purchase guidance.

## Scope

### Catalogue layout and filters

- Keep the existing filter fields, URL query parameters, API requests and
  mobile filter drawer unchanged.
- With filters visible, keep the current catalogue grid: one card on mobile,
  two from `sm`, three from `xl`.
- With desktop filters hidden, use the freed width for four cards from `xl`
  (at least 1280px); keep two cards on smaller layouts. This avoids cramped
  cards and preserves readable 3:4 images.
- Proposed revision: make the desktop filter sidebar sticky below the global
  Header without a scrollbar for the whole panel. The existing category-list
  scrollbar remains only after the user expands/searches a long category list;
  it must not take over normal page scrolling.
- Proposed desktop rule: the complete filter panel is pinned below Header while
  catalogue cards scroll. Its own `max-height` and `overflow-y-auto` are
  removed. Existing collapsible filter groups remain available for compacting
  the panel on a short viewport.
- Mobile remains a normal open/close filter panel; it is not sticky.

### Catalogue pagination

- Replace `Вперед` with `Следующая`; retain `Предыдущая` only when not on the
  first page and `Следующая` only when not on the last page.
- Show a comprehensible compact range: first page, last page, current page and
  immediate neighbours. Insert a non-interactive ellipsis for each omitted
  range. Examples: page 1 of 5 = `1 2 … 5`; page 3 of 5 = `1 2 3 4 5`; page 5
  of 10 = `1 … 4 5 6 … 10`.
- On changing a catalogue page, preserve filters/sort/search in the URL and
  smoothly move the viewport to the catalogue result controls before the new
  list is read. Filter/search/sort changes still reset pagination to page 1.
- Preserve existing loading, error, empty, disabled and keyboard states.

### Sticky side panels

- Apply same revised contract to the existing booking panel on an excursion
  detail page and certificate sidebar: sticky below Header, no viewport cap
  and no whole-panel vertical scroll. Their existing contents remain normal
  document flow inside the pinned card.
- On mobile and tablet below `lg`, both panels stay in normal document flow;
  no content is hidden or made sticky.
- Do not make content blocks, question form or booking modal sticky.

### Certificate sidebar copy and layout

Replace the generic sidebar with this approved-for-review proposal:

> **Подарите впечатления, которые остаются**
>
> Выберите номинал — получатель сам найдёт программу по душе: прогулку по
> Омску, поездку за город или путешествие. Мы поможем оформить подарок и
> договориться о деталях.
>
> **Как это работает**
>
> 1. Оставьте заявку с номиналом и форматом.
> 2. Менеджер уточнит детали и подготовит сертификат.
> 3. Подарите человеку время для новых впечатлений.
>
> **Нужна помощь?**
>
> Позвоните или напишите — помогу выбрать формат и номинал. Номер показывается
> как `+7 … (Ирина Руснак)` и остаётся действующей ссылкой для звонка.

- Keep the existing first contact phone as the actionable `tel:` link and add
  ` (Ирина Руснак)` directly after its visible number; no new contact data is
  invented.
- On desktop this card remains alongside the form; on mobile it follows the
  form in document flow.

## Explicitly unchanged

- Filter values, selection logic, category expansion and reset behaviour.
- Excursion card contents, slot formatting and API pagination contract.
- Certificate form fields, validation, request status and submission flow.
- Header, footer, booking form and question form contents.
- Backend code, migrations, Admin and external services.

## Implementation targets

- `frontend/src/pages/Catalog.tsx`
- `frontend/src/components/catalog/FilterSidebar.tsx`
- `frontend/src/pages/Certificates.tsx`
- `frontend/src/pages/ExcursionDetail.tsx`
- catalogue Playwright tests and new focused browser evidence where needed.

## Acceptance criteria

- At desktop width ≥1280px, hiding filters produces four readable catalogue
  cards in a row; visible filters preserve the current three-column grid.
- Catalogue pagination has Russian labels, clear ellipses and scrolls to the
  result area after a page transition without losing query parameters.
- Catalogue filters, certificate help and the excursion booking panel use the
  same in-layout desktop `sticky` treatment below Header. They stay in their
  grid columns, never overlay content or the footer, and do not gain an
  overall internal scrollbar. Only an expanded long category list may scroll.
- Certificate sidebar uses the approved copy, actionable Irina Rusnak phone
  label and does not change certificate submission behaviour.
- Mobile widths retain usable catalogue/filter, booking and certificate flows.

## Change log

- 2026-11-09: user replaced the personal name in the certificate process with
  the neutral role “Менеджер”; the name is retained only after the contact
  number for attribution.
- 2026-11-09: user rejected whole-panel scrolling and reported that the filter
  panel must remain pinned while the catalogue scrolls. Proposed revision
  removes whole-panel scrolling and retains scrolling only for an expanded
  long category list. Awaiting explicit approval before code changes.
- 2026-11-09: user approved the revision and extended it to certificate and
  excursion booking sidebars. All three panels use sticky positioning without
  a whole-panel scrollbar; only an expanded long category list may scroll.
- 2026-11-09: agent incorrectly generalized the catalogue fixed-panel request
  to certificate and excursion booking panels. User rejected that expansion.
  Final approved split: catalogue filters are fixed for the page; certificate
  and booking panels stay in their layouts with `sticky` below Header and no
  whole-panel scrollbar, preventing Header overlap without covering content.
- 2026-11-09: user rejected catalogue filters overlaying footer. Immediate
  safe rollback restores in-layout sticky filters. Proposed next revision is
  a bounded affix: fixed only while the catalogue section is active, then
  pinned above footer. Awaiting explicit approval before implementing it.
- 2026-11-09: user rejected the bounded-affix visual treatment. Final approved
  approach: catalogue filters use the same in-layout `sticky` pattern as the
  certificate and booking panels — below Header, within their grid column,
  without JavaScript affix behaviour, an overall panel scrollbar or overlay of
  content/footer. The earlier bounded-affix decision is superseded.

## Verification plan

- Frontend lint, TypeScript and production build.
- Existing catalogue filter tests plus focused Playwright checks for grid mode,
  pagination range/query preservation and scroll target.
- Desktop screenshots: catalogue filters shown/hidden, booking panel and
  certificate page. Mobile screenshots: catalogue, booking and certificates.
- Independent review against this plan; attach only relevant evidence to PR.

## Risks

- Sticky elements can overlap Header or become inaccessible on short screens;
  desktop-only sticky positioning and normal mobile flow mitigate this.
- Browser smooth-scroll behaviour must not run for filter updates; it applies
  only to an explicit page transition.
