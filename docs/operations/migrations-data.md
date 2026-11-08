# Migrations and data

- Last verified: 2026-11-08
- Evidence: service directories and Compose commands
- Owner: service implementer

| Area | Migration/tooling | Notes |
| --- | --- | --- |
| Django main service | Django migrations under each app | run through approved service deployment flow |
| Recommender | Alembic `migrations/versions/` | `alembic upgrade head` is service-specific |
| Assistant | Django migrations | includes assistant-owned storage models |
| Seed/demo data | `excursions/management/commands/` | never run against production without explicit approval |

Schema/data change plan must state forward migration, rollback/recovery, data
backfill and verification. Do not edit migration history to “clean up” it.
Binary recommender models and Chroma data are runtime assets, not migrations.
