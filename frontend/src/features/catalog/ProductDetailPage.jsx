import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { catalogClient } from "../../api/catalogClient.js";
import { useAuth } from "../auth/AuthContext.jsx";

// US-003 — Product detail view scenario: images, price breakdown, stock, and
// delivery feasibility for the buyer's PIN code.

const FEASIBILITY_LABEL = {
  feasible: "Deliverable to this PIN code",
  not_feasible: "Not deliverable to this PIN code",
  unknown: "Delivery feasibility unavailable right now",
};

export default function ProductDetailPage() {
  const { productId } = useParams();
  const { session } = useAuth();
  const [pinCode, setPinCode] = useState("");
  const [product, setProduct] = useState(null);
  const [error, setError] = useState(null);

  const load = async (pin) => {
    setError(null);
    try {
      const response = await catalogClient.getProductDetail(productId, pin, session?.token);
      setProduct(response.data);
    } catch (err) {
      setError(err.body?.message || "Product not found.");
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [productId]);

  if (error) return <p className="inline-error">{error}</p>;
  if (!product) return <p>Loading…</p>;

  const { price_breakdown: price } = product;

  return (
    <main className="catalog-shell product-detail">
      <h1>{product.title}</h1>
      {product.images[0] && (
        <img
          src={product.images[0]}
          alt={product.title}
          className="product-detail-image"
          onError={(e) => {
            e.currentTarget.style.display = "none";
          }}
        />
      )}
      <p>{product.description}</p>
      <p>Stock available: {product.stock_quantity}</p>

      <section className="price-breakdown">
        <h2>Price Breakdown</h2>
        <p>Basic price: ₹{price.basic_price.toFixed(2)}</p>
        {price.discounted_price != null && <p>Discounted price: ₹{price.discounted_price.toFixed(2)}</p>}
        <p>Tax: ₹{price.tax.toFixed(2)}</p>
        <p>Delivery charge: ₹{price.delivery_charge.toFixed(2)}</p>
        <p>
          <strong>Total: ₹{price.total.toFixed(2)}</strong>
        </p>
      </section>

      <section className="delivery-feasibility">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            load(pinCode);
          }}
        >
          <label>
            Check delivery for PIN code
            <input value={pinCode} onChange={(e) => setPinCode(e.target.value)} maxLength={10} />
          </label>
          <button type="submit">Check</button>
        </form>
        <p>{FEASIBILITY_LABEL[product.delivery_feasibility]}</p>
      </section>
    </main>
  );
}
