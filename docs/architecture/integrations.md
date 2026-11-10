# Architecture: integrations

- Last verified: 2026-11-08
- Evidence: Compose files and service manifests
- Owner: agent

| Integration | Used by | Contract / safety boundary |
| --- | --- | --- |
| PostgreSQL / pgvector | main service, recommender, assistant | Migrations are service-owned; never share production credentials in docs |
| Redis | main service, recommender, assistant/vectorizer | cache/broker support; health does not prove application correctness |
| RabbitMQ | main service, recommender, vectorizer | async events/jobs must not make user request fail silently |
| Chroma | assistant and vectorizer | persisted Docker volume; runtime data, never commit |
| LLM provider | assistant/vectorizer | environment-backed credentials; document behaviour, not keys |
| YooKassa | main service roadmap | test mode only until separate approved implementation |
| Google/VK auth | accounts/frontend build configuration | client IDs/config are environment-specific |

Production nginx denies public access to recommender maintenance and Django
analytics internal routes. Cross-service callers use internal network paths;
do not expose those endpoints by adding frontend calls.
