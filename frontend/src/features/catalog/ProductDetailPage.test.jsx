import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import ProductDetailPage from "./ProductDetailPage.jsx";
import { AuthProvider } from "../auth/AuthContext.jsx";
import { catalogClient } from "../../api/catalogClient.js";
import { cartClient } from "../../api/cartClient.js";
import { wishlistClient } from "../../api/wishlistClient.js";

vi.mock("../../api/catalogClient.js", () => ({
  catalogClient: { getProductDetail: vi.fn() },
}));
vi.mock("../../api/cartClient.js", () => ({
  cartClient: { addItem: vi.fn() },
}));
vi.mock("../../api/wishlistClient.js", () => ({
  wishlistClient: { addToWishlist: vi.fn() },
}));

function renderPage() {
  return render(
    <AuthProvider>
      <MemoryRouter initialEntries={["/products/1"]}>
        <Routes>
          <Route path="/products/:productId" element={<ProductDetailPage />} />
        </Routes>
      </MemoryRouter>
    </AuthProvider>
  );
}

const baseProduct = {
  id: 1,
  title: "Foldable Lightweight Wheelchair",
  description: "Aluminium-frame foldable wheelchair.",
  stock_quantity: 15,
  images: ["https://example-cdn/wheelchair-1.jpg"],
  price_breakdown: {
    basic_price: 8999,
    discounted_price: null,
    tax: 449.95,
    delivery_charge: 49,
    total: 9497.95,
  },
  delivery_feasibility: "unknown",
};

beforeEach(() => {
  vi.clearAllMocks();
});

describe("ProductDetailPage (US-003)", () => {
  it("renders price breakdown and stock once loaded", async () => {
    catalogClient.getProductDetail.mockResolvedValue({ data: baseProduct });
    renderPage();

    expect(await screen.findByText("Foldable Lightweight Wheelchair")).toBeInTheDocument();
    expect(screen.getByText(/stock available: 15/i)).toBeInTheDocument();
    expect(screen.getByText(/total: ₹9497.95/i)).toBeInTheDocument();
    expect(screen.getByText(/delivery feasibility unavailable/i)).toBeInTheDocument();
  });

  it("shows the discounted price line when present", async () => {
    catalogClient.getProductDetail.mockResolvedValue({
      data: { ...baseProduct, price_breakdown: { ...baseProduct.price_breakdown, discounted_price: 8099.1 } },
    });
    renderPage();
    expect(await screen.findByText(/discounted price: ₹8099.1/i)).toBeInTheDocument();
  });

  it("re-checks feasibility when a PIN code is submitted", async () => {
    catalogClient.getProductDetail
      .mockResolvedValueOnce({ data: baseProduct })
      .mockResolvedValueOnce({ data: { ...baseProduct, delivery_feasibility: "feasible" } });
    const user = userEvent.setup();
    renderPage();
    await screen.findByText("Foldable Lightweight Wheelchair");

    await user.type(screen.getByRole("textbox"), "560001");
    await user.click(screen.getByRole("button", { name: /check/i }));

    await waitFor(() => expect(catalogClient.getProductDetail).toHaveBeenCalledWith("1", "560001", undefined));
    expect(await screen.findByText(/deliverable to this pin code/i)).toBeInTheDocument();
  });

  it("shows an error message when the product cannot be found", async () => {
    catalogClient.getProductDetail.mockRejectedValue({ body: { message: "Product not found." } });
    renderPage();
    expect(await screen.findByText("Product not found.")).toBeInTheDocument();
  });

  it("adds the product to the cart (US-004 entry point)", async () => {
    catalogClient.getProductDetail.mockResolvedValue({ data: baseProduct });
    cartClient.addItem.mockResolvedValue({});
    const user = userEvent.setup();
    renderPage();

    await screen.findByText("Foldable Lightweight Wheelchair");
    await user.click(screen.getByRole("button", { name: /add to cart/i }));

    await waitFor(() => expect(cartClient.addItem).toHaveBeenCalledWith(1, 1, undefined));
    expect(await screen.findByText(/added to cart/i)).toBeInTheDocument();
  });

  it("adds the product to the wishlist (US-004 entry point)", async () => {
    catalogClient.getProductDetail.mockResolvedValue({ data: baseProduct });
    wishlistClient.addToWishlist.mockResolvedValue({});
    const user = userEvent.setup();
    renderPage();

    await screen.findByText("Foldable Lightweight Wheelchair");
    await user.click(screen.getByRole("button", { name: /add to wishlist/i }));

    await waitFor(() => expect(wishlistClient.addToWishlist).toHaveBeenCalledWith(1, undefined));
    expect(await screen.findByText(/added to wishlist/i)).toBeInTheDocument();
  });
});
