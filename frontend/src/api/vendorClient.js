const VENDOR_BASE_URL = import.meta.env.VITE_VENDOR_SERVICE_URL || "http://localhost:8008";

async function request(path, token, options = {}) {
  const res = await fetch(`${VENDOR_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...(options.headers || {}),
    },
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

export const vendorClient = {
  getFormMeta: (token, step) => request(`/api/vendor/onboarding/forms/${step}/meta`, token).then((b) => b.data),

  getForm: (token, step) => request(`/api/vendor/onboarding/forms/${step}`, token).then((b) => b.data),

  saveForm: (token, step, data, version) =>
    request(`/api/vendor/onboarding/forms/${step}`, token, {
      method: "PUT",
      headers: { "If-Match": String(version) },
      body: JSON.stringify(data),
    }).then((b) => b.data),

  presignDocument: (token, step, documentField) =>
    request(`/api/vendor/onboarding/documents/presign?step=${step}`, token, {
      method: "POST",
      body: JSON.stringify({ document_field: documentField }),
    }).then((b) => b.data),

  submit: (token) => request("/api/vendor/onboarding/submit", token, { method: "POST" }).then((b) => b.data),

  getStatus: (token) => request("/api/vendor/onboarding/status", token).then((b) => b.data),

  adminListQueue: (token, filters = {}) => {
    const params = new URLSearchParams(Object.entries(filters).filter(([, v]) => v));
    return request(`/api/admin/vendor-onboarding?${params}`, token).then((b) => b.data);
  },

  adminGetDetail: (token, vendorId) =>
    request(`/api/admin/vendor-onboarding/${vendorId}`, token).then((b) => b.data),

  adminApprove: (token, vendorId, version) =>
    request(`/api/admin/vendor-onboarding/${vendorId}/approve`, token, {
      method: "POST",
      body: JSON.stringify({ version }),
    }).then((b) => b.data),

  adminReject: (token, vendorId, remarks, version) =>
    request(`/api/admin/vendor-onboarding/${vendorId}/reject`, token, {
      method: "POST",
      body: JSON.stringify({ remarks, version }),
    }).then((b) => b.data),

  adminRequestCorrection: (token, vendorId, comments, version) =>
    request(`/api/admin/vendor-onboarding/${vendorId}/request-correction`, token, {
      method: "POST",
      body: JSON.stringify({ comments, version }),
    }).then((b) => b.data),
};
