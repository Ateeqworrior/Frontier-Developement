import React, { useEffect, useState } from "react";
import { authClient } from "../../api/authClient.js";
import { useAuth } from "./AuthContext.jsx";

// Screen 3 — Role-Specific Home (post-login landing).
// This story is responsible only for the JWT-claim-driven redirect + session banner;
// each role's actual home experience is owned by its own EPIC/story (e.g. US-003, US-011).

export default function RoleHomePage() {
  const { session } = useAuth();
  const [me, setMe] = useState(null);

  useEffect(() => {
    if (session) authClient.me(session.token).then(setMe).catch(() => {});
  }, [session]);

  if (!session) return <p>Not logged in.</p>;

  return (
    <main className="auth-shell">
      <div className="session-banner">
        Logged in as <strong>{me?.email || "…"}</strong> — role: <strong>{session.role}</strong>
      </div>
      <p>Welcome to MartSarathi. Role-specific home content is owned by this role's own story.</p>
    </main>
  );
}
