import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { vendorClient } from "../../api/vendorClient.js";
import { useAuth } from "../auth/AuthContext.jsx";

// US-009: Admin views a vendor's full profile/documents and approves, rejects
// (mandatory remarks), or requests correction (per-field/document comments).

export default function AdminVendorDetailPage() {
  const { session } = useAuth();
  const { vendorId } = useParams();
  const [detail, setDetail] = useState(null);
  const [remarks, setRemarks] = useState("");
  const [correctionField, setCorrectionField] = useState("");
  const [correctionComment, setCorrectionComment] = useState("");
  const [actionError, setActionError] = useState(null);

  function reload() {
    vendorClient.adminGetDetail(session.token, vendorId).then(setDetail);
  }

  useEffect(() => {
    if (session) reload();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session, vendorId]);

  if (!session) return <p>Not logged in.</p>;
  if (!detail) return <p>Loading…</p>;

  async function runAction(action) {
    setActionError(null);
    try {
      await action();
      reload();
    } catch (err) {
      setActionError(err.body?.error?.detail || err.message);
    }
  }

  return (
    <main className="catalog-shell">
      <h1>Vendor #{vendorId}</h1>
      <div className="session-banner">
        Status: <strong>{detail.status.status}</strong>
        {detail.status.admin_comment && <p>Last remarks: {detail.status.admin_comment}</p>}
      </div>

      <section>
        <h2>Documents</h2>
        <ul>
          {Object.entries(detail.documents).map(([field, path]) => (
            <li key={field}>
              {field.replace(/_/g, " ")}: {path}
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h2>Status History</h2>
        <ul>
          {detail.status.history.map((h, i) => (
            <li key={i}>
              {h.changed_at}: {h.from_status || "(start)"} → {h.to_status} — {h.action}
              {h.comment && ` (${h.comment})`}
            </li>
          ))}
        </ul>
      </section>

      {actionError && (
        <p className="inline-error" role="alert">
          {actionError}
        </p>
      )}

      <section className="onboarding-actions">
        <button
          type="button"
          onClick={() => runAction(() => vendorClient.adminApprove(session.token, vendorId, detail.status.version))}
        >
          Approve
        </button>

        <div>
          <label>
            Rejection remarks (required)
            <input type="text" value={remarks} onChange={(e) => setRemarks(e.target.value)} />
          </label>
          <button
            type="button"
            onClick={() =>
              runAction(() => vendorClient.adminReject(session.token, vendorId, remarks, detail.status.version))
            }
          >
            Reject
          </button>
        </div>

        <div>
          <label>
            Field/document needing correction
            <input type="text" value={correctionField} onChange={(e) => setCorrectionField(e.target.value)} />
          </label>
          <label>
            Comment
            <input type="text" value={correctionComment} onChange={(e) => setCorrectionComment(e.target.value)} />
          </label>
          <button
            type="button"
            onClick={() =>
              runAction(() =>
                vendorClient.adminRequestCorrection(
                  session.token,
                  vendorId,
                  { [correctionField]: correctionComment },
                  detail.status.version
                )
              )
            }
          >
            Request Correction
          </button>
        </div>
      </section>
    </main>
  );
}
