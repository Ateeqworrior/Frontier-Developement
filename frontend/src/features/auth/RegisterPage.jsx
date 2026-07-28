import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { authClient } from "../../api/authClient.js";
import { useAuth } from "./AuthContext.jsx";

// Screen 1 — Registration Redirect (Role Select).
// docs/design/ui-ux/wireframes/us-001-sso-registration-login.md

const ROLES = ["user", "vendor", "sponsor", "donor"];

export default function RegisterPage() {
  const [role, setRole] = useState(null);
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState("idle"); // idle | loading | error
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { login } = useAuth();

  async function handleContinue(e) {
    e.preventDefault();
    setStatus("loading");
    setError(null);
    try {
      await authClient.register({ email, username, password, role });
      const data = await authClient.login(email, password);
      login(data);
      navigate("/home");
    } catch (err) {
      setStatus("error");
      setError(err.body?.error?.detail || err.message);
    }
  }

  return (
    <main className="auth-shell">
      <a href="#main" className="skip-link">
        Skip to content
      </a>
      <div className="auth-card" id="main">
        <h1>Join MartSarathi</h1>

        <fieldset disabled={status === "loading"}>
          <legend>Select your role</legend>
          <div className="role-selector" role="radiogroup" aria-label="Role">
            {ROLES.map((r) => (
              <label key={r} className={role === r ? "role-option selected" : "role-option"}>
                <input type="radio" name="role" value={r} checked={role === r} onChange={() => setRole(r)} />
                {r.charAt(0).toUpperCase() + r.slice(1)}
              </label>
            ))}
          </div>
        </fieldset>

        <form onSubmit={handleContinue}>
          <label>
            Email
            <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
          </label>
          <label>
            Username
            <input type="text" required value={username} onChange={(e) => setUsername(e.target.value)} />
          </label>
          <label>
            Password
            <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} />
          </label>

          {status === "error" && (
            <p className="inline-error" role="alert">
              {error}
            </p>
          )}

          <button type="submit" disabled={!role || status === "loading"}>
            {status === "loading" ? "Continuing…" : "Continue to registration"}
          </button>
        </form>

        <p>
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </div>
    </main>
  );
}
