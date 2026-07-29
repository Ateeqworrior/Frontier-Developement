# US-004: Cart & Wishlist Management

- **As a** Buyer **I want** to manage a shopping cart and wishlist, and check delivery feasibility **so that** I can prepare my order before checkout with an accurate total.
- **Owns:** `services/cart-service/`
- **Branch:** `feat/cart-wishlist-management`
- **Depends on:** US-003 (products must be discoverable)
- **Satisfies:** FR-04-01, FR-04-02, FR-04-03, FR-04-04, FR-04-05
- **Epic:** EP-04 ([CP-4](https://ateequrrahaman2004.atlassian.net/browse/CP-4))
- **Wave:** 2 — Core Commerce

## Acceptance Criteria (Gherkin)

```gherkin
Feature: Cart & Wishlist

  Scenario: Add to cart
    Given a Buyer is viewing a product
    When they add it to the cart
    Then the cart item count updates and the product appears in the cart

  Scenario: Update or remove cart item
    Given a Buyer has items in the cart
    When they change quantity or remove an item
    Then the cart total (including tax and delivery) recalculates immediately

  Scenario: Delivery feasibility check
    Given a Buyer enters a PIN code in the cart
    Then the system shows whether delivery is feasible to that location

  Scenario: Wishlist to cart
    Given a Buyer has items in their wishlist
    When they move an item to the cart
    Then it is removed from the wishlist and added to the cart
```

## Task Breakdown

1. Cart CRUD API (`/cart/items`) with quantity update and removal.
2. Total calculation service (tax + delivery charge) via Transactional Outbox event or direct call to pricing logic.
3. Delivery-feasibility-by-PIN endpoint (calls EPIC-13 logistics integration).
4. Wishlist CRUD API and move-to-cart action.
5. Frontend: cart drawer/page, wishlist page, PIN-code feasibility widget.
6. Unit + integration tests for total recalculation and wishlist↔cart transitions.
