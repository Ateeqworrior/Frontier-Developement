# TC-001 — Browse by category, filter, and sort

**Automated by:** `test_discovery.py::test_browse_by_category`, `test_discovery.py::test_filter_and_sort_by_price`,
`test_repository_unit.py` (`test_list_products_filters_by_brand`, `test_list_products_filters_by_min_rating`,
`test_list_products_filters_by_price_max`, `test_list_products_sort_price_desc`,
`test_list_products_sort_popularity`, `test_list_products_excludes_unpublished`, `test_pagination_limits_page_size`),
`test_router_integration.py` (`test_sort_by_popularity`, `test_sort_by_price_desc`,
`test_brand_filter_excludes_non_matching_products`, `test_min_rating_filter`, `test_pagination_page_size_is_honored`)

## Steps
1. GET `/api/catalog/products?category_id=` with no other filters — returns only `Published` products
   in that category, paginated.
2. Apply `price_min`/`price_max`, `brand_id`, and `min_rating` filters, individually and combined.
3. Apply each `sort` value (`price_asc`, `price_desc`, `recency`, `popularity`).

## Expected result
- Only `Published` products (never `Draft`) are returned.
- Each filter narrows the result set to exactly the matching products.
- Each sort order returns products in the correct sequence relative to `min_price`/`purchase_count`/`created_at`.
- `pagination.total` reflects the full filtered count, independent of `page_size`.

## Pass/fail criteria
Pass if every filter/sort combination returns the expected product set and order; fail on any
incorrect inclusion/exclusion or ordering.
