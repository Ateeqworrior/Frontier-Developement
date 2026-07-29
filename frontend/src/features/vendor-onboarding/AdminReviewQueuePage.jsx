import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { vendorClient } from "../../api/vendorClient.js";
import { useAuth } from "../auth/AuthContext.jsx";

// US-009: Admin reviews a filterable vendor onboarding queue (status/date/category).

export default function AdminReviewQueuePage() {
  const { session } = useAuth();
  const [entries, setEntries] = useState([]);
  const [status, setStatus] = useState("");
  const [category, setCategory] = useState("");

  useEffect(() => {
    if (!session) return;
    vendorClient.adminListQueue(session.token, { status, category }).then(setEntries);
  }, [session, status, category]);

  if (!session) return <p>Not logged in.</p>;

  return (
    <main className="catalog-shell">
      <h1>Vendor Onboarding Review Queue</h1>

      <div className="catalog-controls">
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="">All statuses</option>
          <option value="Submitted">Submitted</option>
          <option value="Approved">Approved</option>
          <option value="Rejected">Rejected</option>
          <option value="Correction Required">Correction Required</option>
        </select>
        <input
          type="text"
          placeholder="Filter by category"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        />
      </div>

      <table className="onboarding-queue-table">
        <thead>
          <tr>
            <th>Vendor</th>
            <th>Category</th>
            <th>Status</th>
            <th>Submitted</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((entry) => (
            <tr key={entry.vendor_id}>
              <td>
                <Link to={`/admin/vendor-onboarding/${entry.vendor_id}`}>
                  {entry.business_name || `Vendor #${entry.vendor_id}`}
                </Link>
              </td>
              <td>{entry.category || "—"}</td>
              <td>{entry.status}</td>
              <td>{entry.submitted_at ? new Date(entry.submitted_at).toLocaleDateString() : "—"}</td>
            </tr>
          ))}
          {entries.length === 0 && (
            <tr>
              <td colSpan={4}>No vendors match these filters.</td>
            </tr>
          )}
        </tbody>
      </table>
    </main>
  );
}
