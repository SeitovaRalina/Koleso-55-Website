# Production topology and release boundary

- Last verified: 2026-11-08
- Evidence: `backend/compose.production.yml`, `frontend/nginx/default.conf.template`
- Owner: release agent after direct server evidence

Production Compose runs Redis, RabbitMQ, main service, Django workers,
recommender API/worker, assistant, vectorizer and frontend nginx. It uses
named volumes for state, memory limits, restart policy and service health
checks. Nginx terminates TLS, serves frontend/static/media and proxies APIs.

For explicitly authorised production work, also read local gitignored
`production-local.md` when present. It is intentionally absent from Git and
must never be copied into reports, PRs or task systems.

Public proxy rules:

- `/api/` → main service;
- `/api/v1/` → recommender;
- `/api/assistant/` → assistant with rate limit;
- recommender maintenance and analytics internal endpoints return 404 publicly.

Before a release: verify exact commit, database/media backup, free memory/disk,
service health and browser/Admin smoke. Build/recreate only services required
by release; never run broad destructive Compose commands on a live stack.
Production vectorizer/recommender workers need capacity assessment before they
are enabled. Never treat this topology document as authorisation to deploy.
Merge/deploy requires approved review reports for relevant product/code task.
