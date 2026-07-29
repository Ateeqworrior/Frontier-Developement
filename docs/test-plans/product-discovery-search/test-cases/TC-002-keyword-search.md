# TC-002 — Keyword search (relevance-ranked)

**Automated by:** `test_discovery.py::test_keyword_search`, `test_discovery.py::test_search_query_too_short_is_rejected`,
`test_repository_unit.py` (`test_search_matches_description_and_respects_filters`, `test_search_with_no_match_returns_empty`)

## Steps
1. GET `/api/catalog/products/search?q=<term>` where `<term>` matches a product's title/description/tags.
2. GET the same endpoint with filters (`category_id`, `brand_id`) combined with `q`.
3. GET with a `q` shorter than 2 characters.
4. GET with a `q` that matches nothing.

## Expected result
- Matching products are returned (LIKE-based match on SQLite dev/test; MySQL FULLTEXT relevance
  ranking in production per ADR-0002 — see Known Gaps in `test-plan.md`).
- Filters combined with `q` further narrow the result set.
- `q` below the 2-character minimum → `422 invalid_search_query`.
- No match → empty result set, `200 OK` (not an error).

## Pass/fail criteria
Pass if all four cases behave as above; fail on any incorrect status code or result set.
