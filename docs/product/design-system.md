# Design system

- Last verified: 2026-11-08
- Evidence: approved frontend decisions; `frontend/public/hero-bg.jpg`
- Owner: product owner for UX, frontend implementer for code

Direction: premium editorial travel site with clear marketplace catalogue. Photos and route content lead; blue is anchor, not whole surface. Use calm layout, readable Russian labels, strong focus states and mobile-first controls.

Core tokens: sky `#0B8ED8`, deep `#0A3F9A`, mist `#D9EEF7`, green `#6FA36B`, cream `#F4EFE6`, brick `#9B4A31`, ink `#172033`, text `#4B5563`, line `#E5E7EB`. Typical content width 1180px; card image ratio 3:4; controls 44–48px.

Reusable patterns: Button, Badge, Input, Select, Checkbox, Tabs, alert, skeleton, empty/error states, excursion card, filter sidebar and booking panel. `/ui-kit` is dev-only. Do not add shadcn/ui without approval. Contact URLs live in `frontend/src/config/contacts.ts`.
