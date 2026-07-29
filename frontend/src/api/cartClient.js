const CART_BASE_URL = import.meta.env.VITE_CART_SERVICE_URL || "http://localhost:8003/api/cart";

async function request(path, token, { method = "GET", body } = {}) {
  const res = await fetch(`${CART_BASE_URL}${path}`, {
    method,
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  const responseBody = await res.json();
  if (!res.ok) {
    const error = new Error(responseBody.message || "request failed");
    error.status = res.status;
    error.code = responseBody.message_code;
    error.body = responseBody;
    throw error;
  }
  return responseBody;
}

function toQueryString(params) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") search.set(key, value);
  });
  const qs = search.toString();
  return qs ? `?${qs}` : "";
}

export const cartClient = {
  // Scenario: Add to cart (initial view + subsequent reads, includes computed totals).
  getCart: (token) => request("", token),

  // Scenario: Add to cart.
  addItem: (productId, quantity, token) =>
    request("/items", token, { method: "POST", body: { product_id: productId, quantity } }),

  // Scenario: Update or remove cart item — quantity change.
  updateItem: (itemId, quantity, token) =>
    request(`/items/${itemId}`, token, { method: "PUT", body: { quantity } }),

  // Scenario: Update or remove cart item — removal.
  removeItem: (itemId, token) => request(`/items/${itemId}`, token, { method: "DELETE" }),

  setSavedForLater: (itemId, isSavedForLater, token) =>
    request(`/items/${itemId}/save-for-later`, token, {
      method: "PUT",
      body: { is_saved_for_later: isSavedForLater },
    }),

  // Scenario: Delivery feasibility check.
  getDeliveryFeasibility: (pinCode, token) => request(`/delivery-feasibility${toQueryString({ pin_code: pinCode })}`, token),

  // Scenario: Wishlist to cart.
  moveWishlistItemToCart: (wishlistId, token) =>
    request(`/wishlist/${wishlistId}/move-to-cart`, token, { method: "POST" }),
};
