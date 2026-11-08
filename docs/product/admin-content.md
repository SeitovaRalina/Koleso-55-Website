# Django Admin content map

- Last verified: 2026-11-08
- Evidence: main-service app models/admin modules
- Owner: project owner for content; agent for technical mapping

Admin is mounted at `/admin/` by main service. Content/records are organised by
app:

| Area | Admin-managed records |
| --- | --- |
| Accounts | users and staff/group access |
| Excursions | categories, excursions, photos, slots, programme days, ticket types |
| Bookings | tour orders and manager comments/status |
| Reviews | reviews, moderation, homepage selection and review photos |
| Wishlist | user saved excursions |
| Analytics | excursion view records |

Admin labels/settings must be checked in actual `admin.py` and models before
changing copy. This file describes ownership only; it is not a how-to guide for
unverified fields.
