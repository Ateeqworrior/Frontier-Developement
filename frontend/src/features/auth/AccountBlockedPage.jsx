import React from "react";
import { Link } from "react-router-dom";

// Screen 5 — Account Blocked / Auth Error State.
// docs/design/ui-ux/wireframes/us-001-sso-registration-login.md

export default function AccountBlockedPage() {
  return (
    <main className="auth-shell">
      <div className="auth-card error-state-banner" role="alert">
        <h1>Account blocked</h1>
        <p>Your account has been blocked by an administrator. Contact support for assistance.</p>
        <Link to="/support">Contact support</Link>
      </div>
    </main>
  );
}
