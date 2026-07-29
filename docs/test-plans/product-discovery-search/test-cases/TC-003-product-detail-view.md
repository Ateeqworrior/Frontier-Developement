# TC-003 — Product detail view: price breakdown, stock, delivery feasibility

**Automated by:** `test_discovery.py::test_product_detail_view`, `test_services_unit.py`
(`test_get_product_detail_handles_product_with_no_variant`, `test_get_product_detail_not_sponsored_never_discounts`)

## Steps
1. GET `/api/catalog/products/{id}` for a `Published` product with a variant.
2. GET the same endpoint with a `pin_code` query parameter.
3. GET for a product with no variant record.

## Expected result
- Response includes images, description, `stock_quantity` (from the variant), and a
  `price_breakdown` object with `basic_price`, `tax` (5% default), `delivery_charge` (₹49 default),
  and `total = taxable_amount + tax + delivery_charge`.
- `delivery_feasibility` is present (`feasible`/`not_feasible`/`unknown` — see TC-006 for the
  Logistics-client branches this delegates to).
- A product with no variant returns `stock_quantity: 0` and `basic_price: 0.0` rather than erroring.

## Pass/fail criteria
Pass if the price breakdown arithmetic and stock/feasibility fields match expectations; fail on
any incorrect calculation or an unhandled exception for the no-variant case.
