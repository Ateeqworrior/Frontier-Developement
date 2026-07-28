import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import AccountBlockedPage from "./AccountBlockedPage.jsx";

describe("AccountBlockedPage (Screen 5)", () => {
  it("renders the blocked-account message and a support link", () => {
    render(
      <MemoryRouter>
        <AccountBlockedPage />
      </MemoryRouter>
    );
    expect(screen.getByRole("heading", { name: /account blocked/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /contact support/i })).toHaveAttribute("href", "/support");
  });
});
