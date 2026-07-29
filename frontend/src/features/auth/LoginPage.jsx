import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { authClient } from "../../api/authClient.js";
import { useAuth } from "./AuthContext.jsx";

// Screen 2 — Login Redirect.
// docs/design/ui-ux/wireframes/us-001-sso-registration-login.md

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState("idle"); // idle | loading | error
  const navigate = useNavigate();
  const { login } = useAuth();

  async function handleLogin(e) {
    e.preventDefault();
    setStatus("loading");
    try {
      const data = await authClient.login(email, password);
      login(data);
      navigate("/home");
    } catch (err) {
      if (err.code === "account_blocked") {
        navigate("/blocked");
        return;
      }
      setStatus("error");
    }
  }

  return (
    <main className="auth-shell">
      <div className="auth-card">
        <h1>Log in to MartSarathi</h1>

        <form onSubmit={handleLogin}>
          <label>
            Email
            <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
          </label>
          <label>
            Password
            <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} />
          </label>

          {status === "error" && (
            <p className="inline-error" role="alert">
              CARS authentication failed. Please try again.
            </p>
          )}

          <button type="submit" disabled={status === "loading"}>
            {status === "loading" ? "Logging in…" : "Continue with CARS SSO"}
          </button>
        </form>

        <p>
          New here? <Link to="/register">Register</Link>
        </p>
        <p>
          <Link to="/forgot-password">Forgot password?</Link>
        </p>
      </div>
    </main>
  );
}
