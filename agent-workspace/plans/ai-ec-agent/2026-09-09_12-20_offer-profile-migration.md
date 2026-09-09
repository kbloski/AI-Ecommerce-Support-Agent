# Goal

Replace the former Knowledge stage with Knowledge and remove KnowledgeInsights.

# Scope

The change affects the generated profile model, API/routes, frontend navigation, downstream foreign keys, and SQLite migrations. `knowledge_insights` data is intentionally retired.

# Status

- [ ] Map and rename the generated profile stage.
- [ ] Remove KnowledgeInsights across persistence, API, and UI.
- [ ] Migrate the database safely and validate both applications.
