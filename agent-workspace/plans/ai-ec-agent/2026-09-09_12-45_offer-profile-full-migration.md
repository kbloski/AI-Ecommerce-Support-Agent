# Goal

Replace the `Knowledge` aggregate with `OfferProfile` throughout the backend, database, API, and frontend; remove `KnowledgeInsights` entirely.

# Execution Plan

1. [x] Restore a coherent pre-migration source state while preserving the completed OfferRaw work.
2. [x] Rename the ORM aggregate, persistence table, and all foreign-key columns from `knowledge` / `knowledge_id` to `offer_profiles` / `offer_profile_id`.
3. [x] Remove insight models, repositories, DTOs, handlers, endpoints, UI routes, and generated insight payloads.
4. [x] Rename application-layer and frontend identifiers/routes to `OfferProfile` / `offer-profiles`.
5. [x] Add an idempotent SQLite migration that preserves profile and downstream data while removing retired insight data.
6. [x] Validate backend imports/compilation and frontend lint, then record the result.

# Data Handling

Profile data and dependent analysis, audience, and brand-marketing records are preserved. `knowledge_insights` is intentionally dropped.
