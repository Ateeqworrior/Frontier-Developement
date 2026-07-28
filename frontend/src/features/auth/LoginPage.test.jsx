import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import LoginPage from "./LoginPage.jsx";
import { AuthProvider } from "./AuthContext.jsx";
import { authClient } from "../../api/authClient.js";

vi.mock("../../api/authClient.js", () => ({
  authClient: { login: vi.fn() },
}));

const navigateMock = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => navigateMock };
});

function renderPage() {
  return render(
    <AuthProvider>
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    </AuthProvider>
  );
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("LoginPage (Screen 2)", () => {
  it("logs in and navigates to /home on success", async () => {
    authClient.login.mockResolvedValue({ access_token: "t", user_id: 3, role: "vendor" });
    const user = userEvent.setup();
    renderPage();

    await user.type(screen.getByLabelText(/email/i), "v@b.com");
    await user.type(screen.getByLabelText(/password/i), "pw");
    await user.click(screen.getByRole("button", { name: /continue with cars sso/i }));

    await waitFor(() => expect(navigateMock).toHaveBeenCalledWith("/home"));
  });

  it("redirects to /blocked when the account is blocked", async () => {
    authClient.login.mockRejectedValue({ code: "account_blocked" });
    const user = userEvent.setup();
    renderPage();

    await user.type(screen.getByLabelText(/email/i), "blocked@b.com");
    await user.type(screen.getByLabelText(/password/i), "pw");
    await user.click(screen.getByRole("button", { name: /continue with cars sso/i }));

    await waitFor(() => expect(navigateMock).toHaveBeenCalledWith("/blocked"));
  });

  it("shows an inline error for other login failures", async () => {
    authClient.login.mockRejectedValue({ code: "invalid_credentials" });
    const user = userEvent.setup();
    renderPage();

    await user.type(screen.getByLabelText(/email/i), "x@b.com");
    await user.type(screen.getByLabelText(/password/i), "wrong");
    await user.click(screen.getByRole("button", { name: /continue with cars sso/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/CARS authentication failed/i);
    expect(navigateMock).not.toHaveBeenCalledWith("/home");
  });
});
