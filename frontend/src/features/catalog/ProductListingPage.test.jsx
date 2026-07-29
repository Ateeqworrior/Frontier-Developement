import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import ProductListingPage from "./ProductListingPage.jsx";
import { AuthProvider } from "../auth/AuthContext.jsx";
import { catalogClient } from "../../api/catalogClient.js";

vi.mock("../../api/catalogClient.js", () => ({
  catalogClient: { listProducts: vi.fn(), searchProducts: vi.fn() },
}));

function renderPage() {
  return render(
    <AuthProvider>
      <MemoryRouter>
        <ProductListingPage />
      </MemoryRouter>
    </AuthProvider>
  );
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("ProductListingPage (US-003)", () => {
  it("loads and renders products on mount", async () => {
    catalogClient.listProducts.mockResolvedValue({
      data: [{ id: 1, title: "Wheelchair", base_price: 8999, avg_rating: 4.5, rating_count: 12, image_url: null }],
    });
    renderPage();

    expect(await screen.findByText("Wheelchair")).toBeInTheDocument();
    expect(screen.getByText("₹8999.00")).toBeInTheDocument();
    expect(catalogClient.listProducts).toHaveBeenCalledTimes(1);
  });

  it("shows an empty state when no products are returned", async () => {
    catalogClient.listProducts.mockResolvedValue({ data: [] });
    renderPage();
    expect(await screen.findByText(/no products found/i)).toBeInTheDocument();
  });

  it("calls searchProducts instead of listProducts once a query is entered", async () => {
    catalogClient.listProducts.mockResolvedValue({ data: [] });
    catalogClient.searchProducts.mockResolvedValue({
      data: [{ id: 2, title: "Cane", base_price: 699, rating_count: 0 }],
    });
    const user = userEvent.setup();
    renderPage();
    await screen.findByText(/no products found/i);

    await user.type(screen.getByLabelText(/search products/i), "cane");
    await user.click(screen.getByRole("button", { name: /apply/i }));

    await waitFor(() => expect(catalogClient.searchProducts).toHaveBeenCalledWith("cane", expect.any(Object), undefined));
    expect(await screen.findByText("Cane")).toBeInTheDocument();
  });

  it("shows an inline error when loading fails", async () => {
    catalogClient.listProducts.mockRejectedValue({ body: { message: "server exploded" } });
    renderPage();
    expect(await screen.findByText("server exploded")).toBeInTheDocument();
  });
});
