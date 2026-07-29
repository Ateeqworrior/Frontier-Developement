// Wishlist CRUD lives on Catalog Service, not Cart Service — per ADR-0004
// (docs/architecture/adrs/0004-wishlist-ownership-cart-orchestration.md), Cart
// Service only orchestrates the move-to-cart action against this same API.
const WISHLIST_BASE_URL = import.meta.env.VITE_WISHLIST_SERVICE_URL || "http://localhost:8002/api/v1/wishlist";

async function request(path, token, { method = "GET", body } = {}) {
  const res = await fetch(`${WISHLIST_BASE_URL}${path}`, {
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

export const wishlistClient = {
  listWishlist: (token) => request("", token),
  addToWishlist: (productId, token) => request("", token, { method: "POST", body: { product_id: productId } }),
  removeFromWishlist: (wishlistId, token) => request(`/${wishlistId}`, token, { method: "DELETE" }),
};
