# Goal

Replace review-status enums with an `is_reviewed` marker for offer-profile elements and target audiences.

# Implementation Steps

1. [x] Add the persisted boolean and an additive migration for existing SQLite databases.
2. [x] Include the field in element DTOs, mapper, filtering, and endpoint responses.
3. [x] Add checked-state editing, display, and filtering to the elements UI.
4. [x] Apply the same marker to target audiences and remove the shared review-status enum/API.

# Validation

- Compile changed Python modules.
- Verify migration and repository filtering using SQLite in memory.
- Run frontend lint and production build.

# Migration

Existing `review_status` values are retained in the database. During migration, `pending` maps to `false`; every other legacy value maps to `true`.
