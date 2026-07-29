"""Field-level metadata for the 6-step onboarding form (HLD/LLD #10.2).

Single source of truth for three things per FR-09-01/02/11:
- the `GET /forms/{step}/meta` metadata API (field name, type, required)
- real-time per-field validation on save
- submission-gating (which fields/documents are mandatory before Submit)
"""

from dataclasses import dataclass
from typing import Literal

FieldType = Literal["string", "text", "bool", "int", "float", "json", "document"]


@dataclass(frozen=True)
class FieldDef:
    name: str
    type: FieldType
    required: bool


FORM_FIELDS: dict[int, list[FieldDef]] = {
    1: [
        FieldDef("business_name", "string", True),
        FieldDef("business_type", "string", True),
        FieldDef("pan_gst", "string", True),
        FieldDef("registration_info", "json", False),
        FieldDef("contact_person_name", "string", True),
        FieldDef("designation", "string", True),
        FieldDef("phone_number", "string", True),
        FieldDef("email", "string", True),
        FieldDef("alternate_email", "string", False),
        FieldDef("address_line", "text", True),
        FieldDef("city", "string", True),
        FieldDef("pin", "string", True),
        FieldDef("latitude", "float", False),
        FieldDef("longitude", "float", False),
    ],
    2: [
        FieldDef("product_category", "string", True),
        FieldDef("other_description", "text", False),
        FieldDef("target_user_group", "string", True),
        FieldDef("accessibility_features", "json", False),
        FieldDef("compliance", "text", True),
        FieldDef("medical_device_license_number", "string", True),
        FieldDef("product_warranty_details", "text", True),
        FieldDef("iso_ce_isi_certificate_path", "document", True),
    ],
    3: [
        FieldDef("udyam_uam_registration_id", "string", True),
        FieldDef("business_type", "string", False),
        FieldDef("cin_number", "string", False),
        FieldDef("is_business_owned_by_pwd", "bool", False),
        FieldDef("pwd_percentage_in_workforce", "int", False),
        FieldDef("accessibility_measures", "json", False),
        FieldDef("willing_to_employ_more_pwds", "bool", False),
        FieldDef("certificate_12a_80g_csr1_path", "document", True),
        FieldDef("fcra_registration_certificate_path", "document", False),
    ],
    4: [
        FieldDef("bank_account_number", "string", True),
        FieldDef("ifsc_code", "string", True),
        FieldDef("upi_id", "string", True),
        FieldDef("preferred_payment_mode", "string", True),
        FieldDef("registration_id", "string", True),
        FieldDef("type_of_registration", "string", True),
        FieldDef("government_id_type", "string", True),
        FieldDef("government_id_path", "document", True),
        FieldDef("name_as_per_bank_account", "string", True),
        FieldDef("cancelled_cheque_path", "document", True),
        FieldDef("tds_category", "string", True),
        FieldDef("fcra_compliance", "bool", False),
    ],
    5: [
        FieldDef("pan_proof_path", "document", True),
        FieldDef("disability_certificate_udid_path", "document", False),
        FieldDef("business_registration_path", "document", False),
        FieldDef("gst_in_proof_path", "document", False),
        FieldDef("product_compliance_certificate_path", "document", True),
        FieldDef("logo_product_image_path", "document", True),
        FieldDef("iso_ce_isi_certificate_path", "document", True),
        FieldDef("brand_logo_path", "document", True),
        FieldDef("trademark_registration_path", "document", True),
        FieldDef("brand_guidelines_path", "document", False),
    ],
    6: [
        FieldDef("confirm_details_accurate", "bool", True),
        FieldDef("consent_share_information", "bool", True),
        FieldDef("agree_follow_guidelines", "bool", True),
        FieldDef("agree_data_privacy_terms", "bool", True),
        FieldDef("confirm_products_original", "bool", True),
        FieldDef("accept_return_refund_policy", "bool", True),
    ],
}

TOTAL_STEPS = len(FORM_FIELDS)


def fields_for_step(step: int) -> list[FieldDef]:
    return FORM_FIELDS[step]


def is_document_field(step: int, field_name: str) -> bool:
    return any(f.name == field_name and f.type == "document" for f in FORM_FIELDS.get(step, []))
