const AUTH_BASE_URL = import.meta.env.VITE_AUTH_SERVICE_URL || "http://localhost:8001/api/auth";

async function request(path, options = {}) {
  const res = await fetch(`${AUTH_BASE_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  const body = await res.json();
  if (!res.ok) {
    const error = new Error(body.message || "request failed");
    error.status = res.status;
    error.code = body.message_code;
    error.body = body;
    throw error;
  }
  return body.data;
}

export const authClient = {
  // Screen 1: Registration Redirect (Role Select) — normally redirects to CARS;
  // this direct register call is the interim email/password fallback path (BRD risk mitigation).
  register: (payload) => request("/register", { method: "POST", body: JSON.stringify(payload) }),

  // Screens 1/2: obtain the CARS authorize redirect URL.
  getCarsAuthorizeUrl: () => request("/cars/authorize"),

  // Screen 2 -> Screen 3/5: exchange the CARS callback code for a session (or 403 account_blocked).
  exchangeCarsCode: (code) => request(`/cars/callback?code=${encodeURIComponent(code)}`),

  // Fallback direct login (principal-based, matches the existing LLD /login contract).
  login: (email, password) =>
    request("/login", {
      method: "POST",
      body: JSON.stringify({ principal: { email, password, isEnabled: true } }),
    }),

  // Screen 4: UDID Verification Prompt.
  verifyUdid: (token, udidNumber) =>
    request("/verify-udid", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify({ udid_number: udidNumber }),
    }),

  me: (token) => request("/me", { headers: { Authorization: `Bearer ${token}` } }),
};
