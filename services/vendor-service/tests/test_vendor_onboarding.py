"""Tests mirror US-009's Gherkin acceptance criteria one-to-one
(docs/user-stories/stories/domain-vendor-onboarding/US-009-vendor-onboarding-workflow.md)."""

REQUIRED_FORM_DATA = {
    1: {
        "business_name": "Sarthak Mobility Aids",
        "business_type": "Pvt Ltd",
        "pan_gst": "ABCDE1234F",
        "contact_person_name": "Asha Rao",
        "designation": "Founder",
        "phone_number": "9876543210",
        "email": "asha@sarthakmobility.example",
        "address_line": "12 MG Road",
        "city": "Bengaluru",
        "pin": "560001",
    },
    2: {
        "product_category": "Mobility Aids",
        "target_user_group": "PwD_Only",
        "compliance": "ISO 7176 compliant",
        "medical_device_license_number": "MDL-2024-001",
        "product_warranty_details": "2 year manufacturer warranty",
        "iso_ce_isi_certificate_path": "s3://vendor-documents/101/iso_ce_isi_certificate_path/a.pdf",
    },
    3: {
        "udyam_uam_registration_id": "UDYAM-KA-03-0012345",
        "certificate_12a_80g_csr1_path": "s3://vendor-documents/101/certificate_12a_80g_csr1_path/b.pdf",
    },
    4: {
        "bank_account_number": "123456789012",
        "ifsc_code": "SBIN0001234",
        "upi_id": "asha@upi",
        "preferred_payment_mode": "Bank Transfer",
        "registration_id": "REG-001",
        "type_of_registration": "Proprietorship",
        "government_id_type": "Aadhaar",
        "government_id_path": "s3://vendor-documents/101/government_id_path/c.pdf",
        "name_as_per_bank_account": "Asha Rao",
        "cancelled_cheque_path": "s3://vendor-documents/101/cancelled_cheque_path/d.pdf",
        "tds_category": "Individual",
    },
    5: {
        "pan_proof_path": "s3://vendor-documents/101/pan_proof_path/e.pdf",
        "product_compliance_certificate_path": "s3://vendor-documents/101/product_compliance_certificate_path/f.pdf",
        "logo_product_image_path": "s3://vendor-documents/101/logo_product_image_path/g.jpg",
        "iso_ce_isi_certificate_path": "s3://vendor-documents/101/iso_ce_isi_certificate_path/h.pdf",
        "brand_logo_path": "s3://vendor-documents/101/brand_logo_path/i.jpg",
        "trademark_registration_path": "s3://vendor-documents/101/trademark_registration_path/j.pdf",
    },
    6: {
        "confirm_details_accurate": True,
        "consent_share_information": True,
        "agree_follow_guidelines": True,
        "agree_data_privacy_terms": True,
        "confirm_products_original": True,
        "accept_return_refund_policy": True,
    },
}


def _headers(token):
    return {"Authorization": f"Bearer {token}"}


def _current_version(client, headers):
    return client.get("/api/vendor/onboarding/status", headers=headers).json()["data"]["version"]


def _save_step(client, headers, step, data=None):
    version = _current_version(client, headers)
    payload = data if data is not None else REQUIRED_FORM_DATA[step]
    return client.put(
        f"/api/vendor/onboarding/forms/{step}",
        json=payload,
        headers={**headers, "If-Match": str(version)},
    )


def _complete_all_steps(client, headers):
    for step in range(1, 7):
        resp = _save_step(client, headers, step)
        assert resp.status_code == 200, resp.text


def test_save_onboarding_draft(client, vendor_token):
    headers = _headers(vendor_token)
    resp = _save_step(client, headers, 1)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["business_name"] == "Sarthak Mobility Aids"

    status_resp = client.get("/api/vendor/onboarding/status", headers=headers)
    assert status_resp.json()["data"]["status"] == "Draft"
    assert status_resp.json()["data"]["is_completed"] is False


def test_submit_blocked_when_mandatory_fields_missing(client, vendor_token):
    headers = _headers(vendor_token)
    _save_step(client, headers, 1)  # only step 1 completed

    resp = client.post("/api/vendor/onboarding/submit", headers=headers)
    assert resp.status_code == 422
    assert resp.json()["message_code"] == "onboarding_incomplete"


def test_submit_onboarding_for_review(client, vendor_token):
    headers = _headers(vendor_token)
    _complete_all_steps(client, headers)

    resp = client.post("/api/vendor/onboarding/submit", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "Submitted"

    status_resp = client.get("/api/vendor/onboarding/status", headers=headers)
    assert status_resp.json()["data"]["status"] == "Submitted"


def test_admin_reviews_vendor_list_with_filters(client, vendor_token, admin_token):
    headers = _headers(vendor_token)
    _complete_all_steps(client, headers)
    client.post("/api/vendor/onboarding/submit", headers=headers)

    admin_headers = _headers(admin_token)
    resp = client.get("/api/admin/vendor-onboarding?status=Submitted", headers=admin_headers)
    assert resp.status_code == 200
    entries = resp.json()["data"]
    assert any(e["vendor_id"] == 101 for e in entries)
    assert entries[0]["business_name"] == "Sarthak Mobility Aids"
    assert entries[0]["category"] == "Mobility Aids"

    detail_resp = client.get("/api/admin/vendor-onboarding/101", headers=admin_headers)
    assert detail_resp.status_code == 200
    assert detail_resp.json()["data"]["status"]["status"] == "Submitted"
    assert "pan_proof_path" in detail_resp.json()["data"]["documents"]


def test_admin_approves_vendor(client, vendor_token, admin_token):
    headers = _headers(vendor_token)
    _complete_all_steps(client, headers)
    client.post("/api/vendor/onboarding/submit", headers=headers)

    resp = client.post("/api/admin/vendor-onboarding/101/approve", headers=_headers(admin_token))
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "Approved"

    # Approved records are locked for further vendor edits.
    version = _current_version(client, headers)
    locked_resp = client.put(
        "/api/vendor/onboarding/forms/1",
        json=REQUIRED_FORM_DATA[1],
        headers={**headers, "If-Match": str(version)},
    )
    assert locked_resp.status_code == 409
    assert locked_resp.json()["message_code"] == "onboarding_locked"


def test_admin_rejects_vendor_with_mandatory_remarks(client, vendor_token, admin_token):
    headers = _headers(vendor_token)
    _complete_all_steps(client, headers)
    client.post("/api/vendor/onboarding/submit", headers=headers)
    admin_headers = _headers(admin_token)

    missing_remarks_resp = client.post(
        "/api/admin/vendor-onboarding/101/reject", json={"remarks": ""}, headers=admin_headers
    )
    assert missing_remarks_resp.status_code == 422
    assert missing_remarks_resp.json()["message_code"] == "remarks_required"

    resp = client.post(
        "/api/admin/vendor-onboarding/101/reject",
        json={"remarks": "PAN document is unreadable"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "Rejected"


def test_admin_requests_correction_and_vendor_resubmits(client, vendor_token, admin_token):
    headers = _headers(vendor_token)
    _complete_all_steps(client, headers)
    client.post("/api/vendor/onboarding/submit", headers=headers)
    admin_headers = _headers(admin_token)

    missing_comments_resp = client.post(
        "/api/admin/vendor-onboarding/101/request-correction", json={"comments": {}}, headers=admin_headers
    )
    assert missing_comments_resp.status_code == 422
    assert missing_comments_resp.json()["message_code"] == "comments_required"

    resp = client.post(
        "/api/admin/vendor-onboarding/101/request-correction",
        json={"comments": {"pan_gst": "PAN number does not match uploaded proof"}},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "Correction Required"

    # Vendor edits the flagged field and resubmits.
    fixed_data = {**REQUIRED_FORM_DATA[1], "pan_gst": "ZYXWV9876G"}
    save_resp = _save_step(client, headers, 1, fixed_data)
    assert save_resp.status_code == 200

    resubmit_resp = client.post("/api/vendor/onboarding/submit", headers=headers)
    assert resubmit_resp.status_code == 200
    assert resubmit_resp.json()["data"]["status"] == "Submitted"


def test_audit_trail_records_every_status_change(client, vendor_token, admin_token):
    headers = _headers(vendor_token)
    _complete_all_steps(client, headers)
    client.post("/api/vendor/onboarding/submit", headers=headers)
    client.post(
        "/api/admin/vendor-onboarding/101/request-correction",
        json={"comments": {"pan_gst": "recheck"}},
        headers=_headers(admin_token),
    )

    status_resp = client.get("/api/vendor/onboarding/status", headers=headers)
    history = status_resp.json()["data"]["history"]
    assert [h["to_status"] for h in history] == ["Submitted", "Correction Required"]
    assert history[0]["changed_by"] == 101
    assert history[1]["changed_by"] == 1
    assert history[1]["comment"]


def test_optimistic_lock_conflict_on_stale_version(client, vendor_token):
    headers = _headers(vendor_token)
    _save_step(client, headers, 1)  # creates status row at version 0 -> 1

    stale_resp = client.put(
        "/api/vendor/onboarding/forms/1",
        json=REQUIRED_FORM_DATA[1],
        headers={**headers, "If-Match": "0"},  # stale — real version is now 1
    )
    assert stale_resp.status_code == 409
    assert stale_resp.json()["message_code"] == "onboarding_version_conflict"


def test_vendor_can_only_access_own_onboarding_record(client, vendor_token, other_vendor_token):
    _save_step(client, _headers(vendor_token), 1)

    # vendor_id is always taken from the caller's own JWT (never a path param) on
    # vendor-facing endpoints, so a second vendor only ever sees their own blank record.
    other_form_resp = client.get("/api/vendor/onboarding/forms/1", headers=_headers(other_vendor_token))
    assert other_form_resp.status_code == 200
    assert other_form_resp.json()["data"]["business_name"] is None

    admin_view_of_first_vendor = client.get("/api/vendor/onboarding/status", headers=_headers(vendor_token))
    assert admin_view_of_first_vendor.json()["data"]["current_step"] == 1
