import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import CartPage from "./CartPage.jsx";
import { AuthProvider } from "../auth/AuthContext.jsx";
import { cartClient } from "../../api/cartClient.js";

vi.mock("../../api/cartClient.js", () => ({
  cartClient: {
    getCart: vi.fn(),
    updateItem: vi.fn(),
    removeItem: vi.fn(),
    setSavedForLater: vi.fn(),
    getDeliveryFeasibility: vi.fn(),
  },
}));

function renderPage() {
  return render(
    <AuthProvider>
      <MemoryRouter>
        <CartPage />
      </MemoryRouter>
    </AuthProvider>
  );
}

const baseCart = {
  items: [
    { id: 1, product_id: 10, quantity: 2, is_saved_for_later: false, title: "Wheelchair", image_url: null, price: 8999 },
  ],
  totals: { subtotal: 17998, tax: 899.9, delivery_charge: 0, grand_total: 18897.9 },
};

beforeEach(() => {
  vi.clearAllMocks();
});

describe("CartPage (US-004)", () => {
  it("renders cart items and computed totals", async () => {
    cartClient.getCart.mockResolvedValue({ data: baseCart });
    renderPage();

    expect(await screen.findByText("Wheelchair")).toBeInTheDocument();
    expect(screen.getByText(/total: ₹18897.90/i)).toBeInTheDocument();
  });

  it("shows an empty-cart message when there are no active items", async () => {
    cartClient.getCart.mockResolvedValue({ data: { items: [], totals: null } });
    renderPage();
    expect(await screen.findByText(/your cart is empty/i)).toBeInTheDocument();
    expect(screen.getByText(/totals unavailable/i)).toBeInTheDocument();
  });

  it("removes an item when Remove is clicked", async () => {
    cartClient.getCart
      .mockResolvedValueOnce({ data: baseCart })
      .mockResolvedValueOnce({ data: { items: [], totals: null } });
    cartClient.removeItem.mockResolvedValue({});
    const user = userEvent.setup();
    renderPage();

    await screen.findByText("Wheelchair");
    await user.click(screen.getByRole("button", { name: /remove/i }));

    await waitFor(() => expect(cartClient.removeItem).toHaveBeenCalledWith(1, undefined));
    expect(await screen.findByText(/your cart is empty/i)).toBeInTheDocument();
  });

  it("checks delivery feasibility for an entered PIN code", async () => {
    cartClient.getCart.mockResolvedValue({ data: baseCart });
    cartClient.getDeliveryFeasibility.mockResolvedValue({ data: { pin_code: "560001", feasibility: "feasible" } });
    const user = userEvent.setup();
    renderPage();

    await screen.findByText("Wheelchair");
    await user.type(screen.getByRole("textbox"), "560001");
    await user.click(screen.getByRole("button", { name: /check/i }));

    expect(await screen.findByText(/deliverable to this pin code/i)).toBeInTheDocument();
  });
});
