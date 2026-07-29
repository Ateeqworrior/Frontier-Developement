import React from "react";

// Renders one onboarding field based on its metadata (name/type/required) from
// `GET /forms/{step}/meta` — see docs/design/services/vendor-service/api-endpoints.md.

export default function FormFieldInput({ field, value, onChange, onUploadDocument }) {
  const label = field.name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

  if (field.type === "bool") {
    return (
      <label className="onboarding-field onboarding-field-checkbox">
        <input type="checkbox" checked={Boolean(value)} onChange={(e) => onChange(e.target.checked)} />
        {label}
        {field.required && <span className="required-mark"> *</span>}
      </label>
    );
  }

  if (field.type === "document") {
    return (
      <label className="onboarding-field">
        {label}
        {field.required && <span className="required-mark"> *</span>}
        <input
          type="file"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) onUploadDocument(field.name, file);
          }}
        />
        {value && <span className="document-uploaded">Uploaded: {value.split("/").pop()}</span>}
      </label>
    );
  }

  if (field.type === "text") {
    return (
      <label className="onboarding-field">
        {label}
        {field.required && <span className="required-mark"> *</span>}
        <textarea value={value || ""} onChange={(e) => onChange(e.target.value)} rows={3} />
      </label>
    );
  }

  if (field.type === "int" || field.type === "float") {
    return (
      <label className="onboarding-field">
        {label}
        {field.required && <span className="required-mark"> *</span>}
        <input
          type="number"
          value={value ?? ""}
          onChange={(e) => onChange(e.target.value === "" ? null : Number(e.target.value))}
        />
      </label>
    );
  }

  if (field.type === "json") {
    return (
      <label className="onboarding-field">
        {label} (comma-separated)
        <input
          type="text"
          value={Array.isArray(value) ? value.join(", ") : ""}
          onChange={(e) => onChange(e.target.value ? e.target.value.split(",").map((s) => s.trim()) : null)}
        />
      </label>
    );
  }

  return (
    <label className="onboarding-field">
      {label}
      {field.required && <span className="required-mark"> *</span>}
      <input type="text" value={value || ""} onChange={(e) => onChange(e.target.value)} />
    </label>
  );
}
