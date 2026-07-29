import { render, screen } from "@testing-library/react";
import { useEffect } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import RoleHomePage from "./RoleHomePage.jsx";
import { AuthProvider, useAuth } from "./AuthContext.jsx";
import { authClient } from "../../api/authClient.js";

vi.mock("../../api/authClient.js", () => ({
  authClient: { me: vi.fn() },
}));

function LoggedIn({ children }) {
  const { session, login } = useAuth();
  useEffect(() => {
    if (!session) login({ access_token: "tok", user_id: 5, role: "vendor" });
  }, [session, login]);
  if (!session) return null;
  return children;
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("RoleHomePage (Screen 3)", () => {
  it("shows a not-logged-in message with no session", () => {
    render(
      <AuthProvider>
        <RoleHomePage />
      </AuthProvider>
    );
    expect(screen.getByText(/not logged in/i)).toBeInTheDocument();
  });

  it("shows the session banner with role and email once logged in", async () => {
    authClient.me.mockResolvedValue({ email: "vendor@example.com" });
    render(
      <AuthProvider>
        <LoggedIn>
          <RoleHomePage />
        </LoggedIn>
      </AuthProvider>
    );
    expect(await screen.findByText("vendor@example.com")).toBeInTheDocument();
    expect(screen.getByText("vendor")).toBeInTheDocument();
  });
});
