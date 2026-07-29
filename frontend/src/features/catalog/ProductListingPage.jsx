import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { catalogClient } from "../../api/catalogClient.js";
import { useAuth } from "../auth/AuthContext.jsx";

// US-003 — Product Discovery, Search & Filtering.
// Covers: browse-by-category, keyword search, and filter/sort scenarios.

export default function ProductListingPage() {
  const { session } = useAuth();
  const [query, setQuery] = useState("");
  const [filters, setFilters] = useState({
    category_id: "",
    price_min: "",
    price_max: "",
    brand_id: "",
    min_rating: "",
    sort: "recency",
  });
  const [products, setProducts] = useState([]);
  const [error, setError] = useState(null);

  const load = async () => {
    setError(null);
    try {
      const response = query.trim()
        ? await catalogClient.searchProducts(query.trim(), filters, session?.token)
        : await catalogClient.listProducts(filters, session?.token);
      setProducts(response.data);
    } catch (err) {
      setError(err.body?.message || "Could not load products.");
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleFilterChange = (field) => (e) => setFilters({ ...filters, [field]: e.target.value });

  return (
    <main className="catalog-shell">
      <h1>Browse Products</h1>

      <form
        className="catalog-controls"
        onSubmit={(e) => {
          e.preventDefault();
          load();
        }}
      >
        <input
          type="search"
          placeholder="Search products…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          aria-label="Search products"
        />
        <input
          type="number"
          placeholder="Category ID"
          value={filters.category_id}
          onChange={handleFilterChange("category_id")}
        />
        <input type="number" placeholder="Min price" value={filters.price_min} onChange={handleFilterChange("price_min")} />
        <input type="number" placeholder="Max price" value={filters.price_max} onChange={handleFilterChange("price_max")} />
        <input
          type="number"
          placeholder="Min rating"
          min="0"
          max="5"
          step="0.1"
          value={filters.min_rating}
          onChange={handleFilterChange("min_rating")}
        />
        <select value={filters.sort} onChange={handleFilterChange("sort")}>
          <option value="recency">Newest</option>
          <option value="price_asc">Price: Low to High</option>
          <option value="price_desc">Price: High to Low</option>
          <option value="popularity">Popularity</option>
        </select>
        <button type="submit">Apply</button>
      </form>

      {error && <p className="inline-error">{error}</p>}

      <div className="product-grid">
        {products.map((product) => (
          <Link to={`/products/${product.id}`} key={product.id} className="product-card">
            {product.image_url && (
              <img
                src={product.image_url}
                alt={product.title}
                onError={(e) => {
                  e.currentTarget.style.display = "none";
                }}
              />
            )}
            <h3>{product.title}</h3>
            <p className="product-price">₹{product.base_price.toFixed(2)}</p>
            {product.avg_rating != null && (
              <p className="product-rating">
                ★ {product.avg_rating.toFixed(1)} ({product.rating_count})
              </p>
            )}
          </Link>
        ))}
        {products.length === 0 && !error && <p>No products found.</p>}
      </div>
    </main>
  );
}
