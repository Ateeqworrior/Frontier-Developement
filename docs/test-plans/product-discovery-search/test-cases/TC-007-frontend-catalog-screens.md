# TC-007 — Frontend listing + detail page render and interaction behavior

**Automated by:** `ProductListingPage.test.jsx` (all 4 tests), `ProductDetailPage.test.jsx` (all 4 tests),
`catalogClient.test.js` (all 6 tests)

## Steps
1. Render `ProductListingPage` — verify it calls `catalogClient.listProducts` on mount and renders
   returned products; verify an empty result set shows an empty-state message.
2. Type a search query and submit — verify `catalogClient.searchProducts` is called instead of
   `listProducts`, and results render.
3. Force `listProducts` to reject — verify the inline error message renders.
4. Render `ProductDetailPage` for a given product ID — verify price breakdown, stock, and
   delivery-feasibility label render correctly, including the discounted-price line when present.
5. Submit a PIN code on the detail page — verify `catalogClient.getProductDetail` is re-called with
   the PIN code and the feasibility label updates.
6. Force `getProductDetail` to reject — verify the inline error message renders.
7. Unit-test `catalogClient` directly against a mocked `fetch`: query-string construction (omitting
   empty/undefined filters), `Authorization` header presence/absence, and error propagation
   (`status`/`code`/`body` on the thrown error).

## Expected result
All steps behave as described; no unhandled promise rejections or console errors beyond the
expected React Router future-flag warnings (pre-existing, unrelated to this story).

## Pass/fail criteria
Pass if all 14 tests across the three files pass; fail on any assertion failure or unhandled error.
