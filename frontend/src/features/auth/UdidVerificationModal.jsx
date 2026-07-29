import React, { useState } from "react";
import { authClient } from "../../api/authClient.js";
import { useAuth } from "./AuthContext.jsx";

// Screen 4 — UDID Verification Prompt.
// docs/design/ui-ux/wireframes/us-001-sso-registration-login.md

export default function UdidVerificationModal({ onResolved }) {
  const { session } = useAuth();
  const [udid, setUdid] = useState("");
  const [status, setStatus] = useState("idle"); // idle | loading | success | error
  const [error, setError] = useState(null);

  async function handleVerify(e) {
    e.preventDefault();
    setStatus("loading");
    setError(null);
    try {
      const data = await authClient.verifyUdid(session.token, udid);
      setStatus("success");
      onResolved?.(data.udid_verified);
    } catch (err) {
      setStatus("error");
      setError(err.body?.error?.detail || "UDID verification failed.");
    }
  }

  return (
    <div className="modal-overlay">
      <div className="modal" role="dialog" aria-modal="true" aria-labelledby="udid-modal-title">
        <h2 id="udid-modal-title">Verify your UDID to unlock sponsored pricing</h2>
        <p>We'll check your UDID against the Sarthak Foundation registry.</p>

        <form onSubmit={handleVerify}>
          <label>
            UDID
            <input
              type="text"
              value={udid}
              onChange={(e) => setUdid(e.target.value)}
              disabled={status === "loading"}
              aria-invalid={status === "error"}
            />
          </label>

          {status === "error" && (
            <p className="inline-error" role="alert">
              {error}
            </p>
          )}

          <button type="submit" disabled={!udid || status === "loading"}>
            {status === "loading" ? "Verifying…" : "Verify"}
          </button>
        </form>

        <button type="button" className="text-link" onClick={() => onResolved?.(false)}>
          Skip — pay full price
        </button>
      </div>
    </div>
  );
}
