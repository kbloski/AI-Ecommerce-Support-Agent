# Goal

Add server-side filtering, newest-first sorting, and pagination to offer-profile elements.

# Context

The UI reference is used only as a visual guide. Offer-profile elements currently load as one unfiltered list.

# Proposed Approach

1. [x] Reuse `common/results/PaginatedResult` as the common backend response model.
2. [x] Add a filtered, paginated repository query and expose it through the existing elements endpoint.
3. [x] Update the RTK Query contract and rebuild the elements view with filter, sorting, and pagination controls.

# Validation

- Compile changed Python modules.
- Run frontend lint and production build.

# Result

- The default order is `created_at DESC`, with `id DESC` as a stable tie-breaker.
- The elements endpoint returns page metadata and requests are renewed when filters, sort order, or page change.
