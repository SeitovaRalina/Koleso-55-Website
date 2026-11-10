# API documentation

`api/contracts.md` is human-maintained route inventory. Django exposes live
OpenAPI at `/api/schema/`, Swagger at `/api/docs/` and Redoc at `/api/redoc/`
when main service is running. That live schema is authoritative for field-level
Django request/response shapes.

Recommender and assistant contracts are documented from source routes until a
generated schema snapshot is separately approved. Do not copy access tokens,
customer payloads or production URLs into API documentation.
