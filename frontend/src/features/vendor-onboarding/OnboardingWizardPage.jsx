import React, { useEffect, useState } from "react";
import { vendorClient } from "../../api/vendorClient.js";
import { useAuth } from "../auth/AuthContext.jsx";
import FormFieldInput from "./FormFieldInput.jsx";

// US-009: 6-step vendor onboarding wizard — save draft/resume, submit for review,
// track status and admin remarks, edit-and-resubmit on correction.
// docs/user-stories/stories/domain-vendor-onboarding/US-009-vendor-onboarding-workflow.md

const STEP_TITLES = {
  1: "Basic Info",
  2: "Product & Service",
  3: "Profile & Inclusion",
  4: "Payment & Compliance",
  5: "Documents",
  6: "Legal & Compliance",
};
const TOTAL_STEPS = Object.keys(STEP_TITLES).length;

export default function OnboardingWizardPage() {
  const { session } = useAuth();
  const [step, setStep] = useState(1);
  const [meta, setMeta] = useState(null);
  const [values, setValues] = useState({});
  const [statusData, setStatusData] = useState(null);
  const [saveState, setSaveState] = useState("idle"); // idle | saving | saved | error | conflict
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!session) return;
    vendorClient.getStatus(session.token).then(setStatusData);
  }, [session]);

  useEffect(() => {
    if (!session) return;
    Promise.all([vendorClient.getFormMeta(session.token, step), vendorClient.getForm(session.token, step)]).then(
      ([metaData, formData]) => {
        setMeta(metaData);
        setValues(formData);
      }
    );
  }, [session, step]);

  if (!session) return <p>Not logged in.</p>;

  const locked = statusData && ["Approved", "Rejected"].includes(statusData.status);

  async function handleUploadDocument(fieldName, file) {
    const presign = await vendorClient.presignDocument(session.token, step, fieldName);
    // Dev stub: real integration would PUT `file` to presign.upload_url before storing the key.
    setValues((prev) => ({ ...prev, [fieldName]: presign.s3_key }));
  }

  async function handleSave(advance) {
    setSaveState("saving");
    setError(null);
    try {
      const version = statusData?.version ?? 0;
      const saved = await vendorClient.saveForm(session.token, step, values, version);
      const newVersion = saved.version;
      setValues(saved);
      const refreshed = await vendorClient.getStatus(session.token);
      setStatusData(refreshed);
      setSaveState("saved");
      if (advance && step < TOTAL_STEPS) setStep(step + 1);
    } catch (err) {
      setSaveState(err.code === "onboarding_version_conflict" ? "conflict" : "error");
      setError(err.body?.error?.detail || err.message);
      if (err.code === "onboarding_version_conflict") {
        const refreshed = await vendorClient.getStatus(session.token);
        setStatusData(refreshed);
      }
    }
  }

  async function handleSubmit() {
    setSaveState("saving");
    setError(null);
    try {
      const status = await vendorClient.submit(session.token);
      setStatusData(status);
      setSaveState("saved");
    } catch (err) {
      setSaveState("error");
      setError(err.body?.error?.detail || err.message);
    }
  }

  return (
    <main className="onboarding-shell">
      <h1>Vendor Onboarding</h1>

      {statusData && (
        <div className="session-banner">
          Status: <strong>{statusData.status}</strong>
          {statusData.admin_comment && <p>Admin remarks: {statusData.admin_comment}</p>}
        </div>
      )}

      <nav className="onboarding-steps" aria-label="Onboarding steps">
        {Object.entries(STEP_TITLES).map(([n, title]) => (
          <button
            key={n}
            className={Number(n) === step ? "onboarding-step active" : "onboarding-step"}
            onClick={() => setStep(Number(n))}
          >
            {n}. {title}
          </button>
        ))}
      </nav>

      {locked && <p className="inline-error">This onboarding record is locked for edits.</p>}

      {meta && (
        <fieldset disabled={locked || saveState === "saving"}>
          <legend>{STEP_TITLES[step]}</legend>
          {meta.fields.map((field) => (
            <FormFieldInput
              key={field.name}
              field={field}
              value={values[field.name]}
              onChange={(v) => setValues((prev) => ({ ...prev, [field.name]: v }))}
              onUploadDocument={handleUploadDocument}
            />
          ))}
        </fieldset>
      )}

      {saveState === "conflict" && (
        <p className="inline-error" role="alert">
          This form was updated elsewhere — latest values reloaded. Please review and save again.
        </p>
      )}
      {saveState === "error" && (
        <p className="inline-error" role="alert">
          {error}
        </p>
      )}

      <div className="onboarding-actions">
        <button type="button" onClick={() => handleSave(false)} disabled={locked || saveState === "saving"}>
          Save Draft
        </button>
        {step < TOTAL_STEPS && (
          <button type="button" onClick={() => handleSave(true)} disabled={locked || saveState === "saving"}>
            Save & Next
          </button>
        )}
        {step === TOTAL_STEPS && (
          <button type="button" onClick={handleSubmit} disabled={locked || saveState === "saving"}>
            Submit for Review
          </button>
        )}
      </div>
    </main>
  );
}
