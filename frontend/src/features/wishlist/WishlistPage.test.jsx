import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import WishlistPage from "./WishlistPage.jsx";
import { AuthProvider } from "../auth/AuthContext.jsx";
import { wishlistClient } from "../../api/wishlistClient.js";
import { cartClient } from "../../api/cartClient.js";

vi.mock("../../api/wishlistClient.js", () => ({
  wishlistClient: { listWishlist: vi.fn(), removeFromWishlist: vi.fn() },
}));
vi.mock("../../api/cartClient.js", () => ({
  cartClient: { moveWishlistItemToCart: vi.fn() },
}));

function renderPage() {
  return render(
    <AuthProvider>
      <MemoryRouter>
        <WishlistPage />
      </MemoryRouter>
    </AuthProvider>
  );
}

const baseItems = [{ id: 101, product_id: 1, title: "Wheelchair", image_url: null, price: 8999 }];

beforeEach(() => {
  vi.clearAllMocks();
});

describe("WishlistPage (US-004)", () => {
  it("renders wishlist items", async () => {
    wishlistClient.listWishlist.mockResolvedValue({ data: baseItems });
    renderPage();
    expect(await screen.findByText("Wheelchair")).toBeInTheDocument();
  });

  it("shows an empty-wishlist message when there are no items", async () => {
    wishlistClient.listWishlist.mockResolvedValue({ data: [] });
    renderPage();
    expect(await screen.findByText(/your wishlist is empty/i)).toBeInTheDocument();
  });

  it("moves an item to the cart and removes it from the wishlist list", async () => {
    wishlistClient.listWishlist
      .mockResolvedValueOnce({ data: baseItems })
      .mockResolvedValueOnce({ data: [] });
    cartClient.moveWishlistItemToCart.mockResolvedValue({
      data: { cart_item: { id: 1, product_id: 1 }, wishlist_removed: true },
    });
    const user = userEvent.setup();
    renderPage();

    await screen.findByText("Wheelchair");
    await user.click(screen.getByRole("button", { name: /move to cart/i }));

    await waitFor(() => expect(cartClient.moveWishlistItemToCart).toHaveBeenCalledWith(101, undefined));
    expect(await screen.findByText(/moved to cart/i)).toBeInTheDocument();
    expect(await screen.findByText(/your wishlist is empty/i)).toBeInTheDocument();
  });

  it("shows a correction message when the move succeeds but wishlist removal fails", async () => {
    wishlistClient.listWishlist.mockResolvedValue({ data: baseItems });
    cartClient.moveWishlistItemToCart.mockResolvedValue({
      data: { cart_item: { id: 1, product_id: 1 }, wishlist_removed: false },
    });
    const user = userEvent.setup();
    renderPage();

    await screen.findByText("Wheelchair");
    await user.click(screen.getByRole("button", { name: /move to cart/i }));

    expect(await screen.findByText(/couldn't remove it from your wishlist/i)).toBeInTheDocument();
  });

  it("removes an item when Remove is clicked", async () => {
    wishlistClient.listWishlist
      .mockResolvedValueOnce({ data: baseItems })
      .mockResolvedValueOnce({ data: [] });
    wishlistClient.removeFromWishlist.mockResolvedValue({});
    const user = userEvent.setup();
    renderPage();

    await screen.findByText("Wheelchair");
    await user.click(screen.getByRole("button", { name: /^remove$/i }));

    await waitFor(() => expect(wishlistClient.removeFromWishlist).toHaveBeenCalledWith(101, undefined));
    expect(await screen.findByText(/your wishlist is empty/i)).toBeInTheDocument();
  });
});
