import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useEffect } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import UdidVerificationModal from "./UdidVerificationModal.jsx";
import { AuthProvider, useAuth } from "./AuthContext.jsx";
import { authClient } from "../../api/authClient.js";

vi.mock("../../api/authClient.js", () => ({
  authClient: { verifyUdid: vi.fn() },
}));

function LoggedInModal({ onResolved }) {
  const { session, login } = useAuth();
  useEffect(() => {
    if (!session) login({ access_token: "tok", user_id: 1, role: "user" });
  }, [session, login]);
  if (!session) return null;
  return <UdidVerificationModal onResolved={onResolved} />;
}

function renderModal(onResolved = vi.fn()) {
  render(
    <AuthProvider>
      <LoggedInModal onResolved={onResolved} />
    </AuthProvider>
  );
  return onResolved;
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("UdidVerificationModal (Screen 4)", () => {
  it("verifies successfully and calls onResolved(true)", async () => {
    authClient.verifyUdid.mockResolvedValue({ udid_verified: true });
    const onResolved = vi.fn();
    renderModal(onResolved);
    const user = userEvent.setup();

    await user.type(screen.getByRole("textbox"), "SF-12345");
    await user.click(screen.getByRole("button", { name: /^verify$/i }));

    expect(await screen.findByRole("button", { name: /^verify$/i })).toBeEnabled();
    expect(onResolved).toHaveBeenCalledWith(true);
  });

  it("shows an inline error on verification failure", async () => {
    authClient.verifyUdid.mockRejectedValue({ body: { error: { detail: "UDID did not match" } } });
    const onResolved = vi.fn();
    renderModal(onResolved);
    const user = userEvent.setup();

    await user.type(screen.getByRole("textbox"), "NOT-A-MATCH");
    await user.click(screen.getByRole("button", { name: /^verify$/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent("UDID did not match");
    expect(onResolved).not.toHaveBeenCalled();
  });

  it("allows skipping verification via onResolved(false)", async () => {
    const onResolved = vi.fn();
    renderModal(onResolved);
    const user = userEvent.setup();

    await user.click(screen.getByRole("button", { name: /skip/i }));
    expect(onResolved).toHaveBeenCalledWith(false);
  });
});
