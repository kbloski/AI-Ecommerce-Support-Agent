# Goal

Replace the persistence model for manually entered offers with `OfferRaw` / `offers_raw`, and remove offer pricing, items, and insights across the backend and frontend.

# Current State

`Offer` is stored in `offers`; it exposes `buying_price`, `selling_price`, `offer_items`, and `offer_insights`. Existing `knowledge.offer_id` records refer to it.

# Implementation Steps

- [x] Remove the obsolete Offer fields and child resources from API, ORM, UI, DI, and supporting scripts.
- [x] Rename the ORM model/table to `OfferRaw` / `offers_raw` and update the `Knowledge` foreign key.
- [x] Add an idempotent SQLite startup migration that preserves offers and knowledge, drops the retired child tables, and removes retired columns.
- [x] Validate Python imports and run frontend lint/type checks.
- [ ] Update persistent project context.

# Risks

Dropping `offer_items`, `offer_insights`, and price columns intentionally discards their existing data. The migration must run before SQLAlchemy creates the new schema.

# Validation

Use an isolated SQLite database seeded with the legacy schema; then verify the renamed table, removed tables/columns, and preserved knowledge relation. Run the frontend lint command.
