const CATALOG_BASE_URL = import.meta.env.VITE_CATALOG_SERVICE_URL || "http://localhost:8002/api/catalog";

async function request(path, token) {
  const res = await fetch(`${CATALOG_BASE_URL}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  const body = await res.json();
  if (!res.ok) {
    const error = new Error(body.message || "request failed");
    error.status = res.status;
    error.code = body.message_code;
    error.body = body;
    throw error;
  }
  return body;
}

function toQueryString(params) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") search.set(key, value);
  });
  const qs = search.toString();
  return qs ? `?${qs}` : "";
}

export const catalogClient = {
  // Scenario: Browse by category / Filter and sort.
  listProducts: (filters = {}, token) => request(`/products${toQueryString(filters)}`, token),

  // Scenario: Keyword search.
  searchProducts: (q, filters = {}, token) => request(`/products/search${toQueryString({ q, ...filters })}`, token),

  // Scenario: Product detail view.
  getProductDetail: (productId, pinCode, token) =>
    request(`/products/${productId}${toQueryString({ pin_code: pinCode })}`, token),
};
