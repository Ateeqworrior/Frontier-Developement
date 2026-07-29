import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { wishlistClient } from "../../api/wishlistClient.js";
import { cartClient } from "../../api/cartClient.js";
import { useAuth } from "../auth/AuthContext.jsx";

// US-004 — Wishlist to cart scenario: move a wishlist item into the cart,
// removing it from the wishlist.

export default function WishlistPage() {
  const { session } = useAuth();
  const [items, setItems] = useState([]);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);

  const load = async () => {
    setError(null);
    try {
      const response = await wishlistClient.listWishlist(session?.token);
      setItems(response.data);
    } catch (err) {
      setError(err.body?.message || "Could not load wishlist.");
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const remove = async (wishlistId) => {
    await wishlistClient.removeFromWishlist(wishlistId, session?.token);
    load();
  };

  const moveToCart = async (wishlistId) => {
    setMessage(null);
    try {
      const response = await cartClient.moveWishlistItemToCart(wishlistId, session?.token);
      setMessage(
        response.data.wishlist_removed
          ? "Moved to cart."
          : "Added to cart, but couldn't remove it from your wishlist — please remove it manually."
      );
      load();
    } catch (err) {
      setError(err.body?.message || "Could not move item to cart.");
    }
  };

  return (
    <main className="wishlist-shell">
      <h1>Your Wishlist</h1>
      {error && <p className="inline-error">{error}</p>}
      {message && <p className="inline-message">{message}</p>}

      {items.length === 0 && !error && <p>Your wishlist is empty.</p>}

      <ul className="wishlist-items">
        {items.map((item) => (
          <li key={item.id} className="wishlist-item">
            {item.image_url && <img src={item.image_url} alt={item.title} />}
            <div className="wishlist-item-details">
              <Link to={`/products/${item.product_id}`}>{item.title}</Link>
              <p>₹{item.price.toFixed(2)}</p>
              <button type="button" onClick={() => moveToCart(item.id)}>
                Move to cart
              </button>
              <button type="button" onClick={() => remove(item.id)}>
                Remove
              </button>
            </div>
          </li>
        ))}
      </ul>
    </main>
  );
}
