import React, { useEffect, useState } from "react";
import { cartClient } from "../../api/cartClient.js";
import { useAuth } from "../auth/AuthContext.jsx";

// US-004 — Cart & Wishlist Management.
// Covers: add/update/remove cart item, total recalculation, and delivery
// feasibility-by-PIN scenarios.

const FEASIBILITY_LABEL = {
  feasible: "Deliverable to this PIN code",
  not_feasible: "Not deliverable to this PIN code",
  unknown: "Delivery feasibility unavailable right now",
};

export default function CartPage() {
  const { session } = useAuth();
  const [cart, setCart] = useState(null);
  const [error, setError] = useState(null);
  const [pinCode, setPinCode] = useState("");
  const [feasibility, setFeasibility] = useState(null);

  const load = async () => {
    setError(null);
    try {
      const response = await cartClient.getCart(session?.token);
      setCart(response.data);
    } catch (err) {
      setError(err.body?.message || "Could not load cart.");
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const updateQuantity = async (itemId, quantity) => {
    if (quantity < 1) return;
    await cartClient.updateItem(itemId, quantity, session?.token);
    load();
  };

  const removeItem = async (itemId) => {
    await cartClient.removeItem(itemId, session?.token);
    load();
  };

  const toggleSavedForLater = async (itemId, isSavedForLater) => {
    await cartClient.setSavedForLater(itemId, isSavedForLater, session?.token);
    load();
  };

  const checkFeasibility = async (e) => {
    e.preventDefault();
    try {
      const response = await cartClient.getDeliveryFeasibility(pinCode, session?.token);
      setFeasibility(response.data.feasibility);
    } catch (err) {
      setError(err.body?.message || "Could not check delivery feasibility.");
    }
  };

  if (error) return <p className="inline-error">{error}</p>;
  if (!cart) return <p>Loading…</p>;

  const activeItems = cart.items.filter((item) => !item.is_saved_for_later);
  const savedItems = cart.items.filter((item) => item.is_saved_for_later);

  return (
    <main className="cart-shell">
      <h1>Your Cart</h1>

      {activeItems.length === 0 && <p>Your cart is empty.</p>}

      <ul className="cart-items">
        {activeItems.map((item) => (
          <li key={item.id} className="cart-item">
            {item.image_url && <img src={item.image_url} alt={item.title} />}
            <div className="cart-item-details">
              <h3>{item.title || `Product #${item.product_id}`}</h3>
              {item.price != null && <p>₹{item.price.toFixed(2)}</p>}
              <label>
                Qty
                <input
                  type="number"
                  min="1"
                  value={item.quantity}
                  onChange={(e) => updateQuantity(item.id, Number(e.target.value))}
                />
              </label>
              <button type="button" onClick={() => toggleSavedForLater(item.id, true)}>
                Save for later
              </button>
              <button type="button" onClick={() => removeItem(item.id)}>
                Remove
              </button>
            </div>
          </li>
        ))}
      </ul>

      {savedItems.length > 0 && (
        <section className="saved-for-later">
          <h2>Saved for later</h2>
          <ul>
            {savedItems.map((item) => (
              <li key={item.id}>
                {item.title || `Product #${item.product_id}`}
                <button type="button" onClick={() => toggleSavedForLater(item.id, false)}>
                  Move to cart
                </button>
                <button type="button" onClick={() => removeItem(item.id)}>
                  Remove
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="cart-totals">
        <h2>Order Summary</h2>
        {cart.totals ? (
          <>
            <p>Subtotal: ₹{cart.totals.subtotal.toFixed(2)}</p>
            <p>Tax: ₹{cart.totals.tax.toFixed(2)}</p>
            <p>Delivery: ₹{cart.totals.delivery_charge.toFixed(2)}</p>
            <p>
              <strong>Total: ₹{cart.totals.grand_total.toFixed(2)}</strong>
            </p>
          </>
        ) : (
          <p>Totals unavailable right now — pricing service is temporarily unreachable.</p>
        )}
      </section>

      <section className="delivery-feasibility">
        <form onSubmit={checkFeasibility}>
          <label>
            Check delivery for PIN code
            <input value={pinCode} onChange={(e) => setPinCode(e.target.value)} maxLength={10} />
          </label>
          <button type="submit">Check</button>
        </form>
        {feasibility && <p>{FEASIBILITY_LABEL[feasibility]}</p>}
      </section>
    </main>
  );
}
