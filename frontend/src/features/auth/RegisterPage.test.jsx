import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import RegisterPage from "./RegisterPage.jsx";
import { AuthProvider } from "./AuthContext.jsx";
import { authClient } from "../../api/authClient.js";

vi.mock("../../api/authClient.js", () => ({
  authClient: { register: vi.fn(), login: vi.fn() },
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
        <RegisterPage />
      </MemoryRouter>
    </AuthProvider>
  );
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("RegisterPage (Screen 1)", () => {
  it("disables submit until a role is selected", () => {
    renderPage();
    expect(screen.getByRole("button", { name: /continue to registration/i })).toBeDisabled();
  });

  it("registers, logs in, and navigates to /home on success", async () => {
    authClient.register.mockResolvedValue({ id: 1, email: "a@b.com" });
    authClient.login.mockResolvedValue({ access_token: "t", user_id: 1, role: "user" });
    const user = userEvent.setup();
    renderPage();

    await user.click(screen.getByLabelText(/^user$/i));
    await user.type(screen.getByLabelText(/email/i), "a@b.com");
    await user.type(screen.getByLabelText(/username/i), "auser");
    await user.type(screen.getByLabelText(/password/i), "S3cure!Pass");
    await user.click(screen.getByRole("button", { name: /continue to registration/i }));

    await waitFor(() => expect(navigateMock).toHaveBeenCalledWith("/home"));
    expect(authClient.register).toHaveBeenCalledWith({
      email: "a@b.com",
      username: "auser",
      password: "S3cure!Pass",
      role: "user",
    });
  });

  it("shows an inline error when registration fails", async () => {
    authClient.register.mockRejectedValue({
      message: "duplicate",
      body: { error: { detail: "email already registered" } },
    });
    const user = userEvent.setup();
    renderPage();

    await user.click(screen.getByLabelText(/^user$/i));
    await user.type(screen.getByLabelText(/email/i), "a@b.com");
    await user.type(screen.getByLabelText(/username/i), "auser");
    await user.type(screen.getByLabelText(/password/i), "S3cure!Pass");
    await user.click(screen.getByRole("button", { name: /continue to registration/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent("email already registered");
    expect(navigateMock).not.toHaveBeenCalled();
  });
});
