from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class VendorOnboardingBasic(Base):
    """Form 1: Basic Info (HLD/LLD #10.2)."""

    __tablename__ = "vendor_onboarding_basic"

    vendor_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    business_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    business_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    pan_gst: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    registration_info: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    contact_person_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    designation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    alternate_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address_line: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    pin: Mapped[Optional[str]] = mapped_column(String(6), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)


class VendorProductService(Base):
    """Form 2: Product & Service (HLD/LLD #10.2)."""

    __tablename__ = "vendor_product_service"

    vendor_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    other_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_user_group: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    accessibility_features: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    compliance: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    medical_device_license_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    product_warranty_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    iso_ce_isi_certificate_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)


class VendorProfileInclusion(Base):
    """Form 3: Profile & Inclusion (HLD/LLD #10.2)."""

    __tablename__ = "vendor_profile_inclusion"

    vendor_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    udyam_uam_registration_id: Mapped[Optional[str]] = mapped_column(String(19), nullable=True)
    business_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    cin_number: Mapped[Optional[str]] = mapped_column(String(21), nullable=True)
    is_business_owned_by_pwd: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    pwd_percentage_in_workforce: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    accessibility_measures: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    willing_to_employ_more_pwds: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    certificate_12a_80g_csr1_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    fcra_registration_certificate_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)


class VendorPaymentCompliance(Base):
    """Form 4: Payment & Compliance (HLD/LLD #10.2)."""

    __tablename__ = "vendor_payment_compliance"

    vendor_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bank_account_number: Mapped[Optional[str]] = mapped_column(String(18), nullable=True)
    ifsc_code: Mapped[Optional[str]] = mapped_column(String(11), nullable=True)
    upi_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    preferred_payment_mode: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    registration_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    type_of_registration: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    government_id_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    government_id_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    name_as_per_bank_account: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    cancelled_cheque_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    tds_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    fcra_compliance: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)


class VendorDocuments(Base):
    """Form 5: Documents (HLD/LLD #10.2)."""

    __tablename__ = "vendor_documents"

    vendor_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pan_proof_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    disability_certificate_udid_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    business_registration_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    gst_in_proof_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    product_compliance_certificate_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    logo_product_image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    iso_ce_isi_certificate_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    brand_logo_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    trademark_registration_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    brand_guidelines_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)


class VendorLegalCompliance(Base):
    """Form 6: Legal & Compliance (HLD/LLD #10.2)."""

    __tablename__ = "vendor_legal_compliance"

    vendor_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    confirm_details_accurate: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    consent_share_information: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    agree_follow_guidelines: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    agree_data_privacy_terms: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    confirm_products_original: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    accept_return_refund_policy: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)


class VendorOnboardingStatus(Base):
    """HLD/LLD #10.3, plus the additive `version` column (ADR-0003)."""

    __tablename__ = "vendor_onboarding_status"

    vendor_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    current_step: Mapped[int] = mapped_column(Integer, default=1)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    # Simplified 5-state model covering every Gherkin scenario for this story:
    # Draft -> Submitted -> Approved | Rejected | Correction Required -> (edit) -> Submitted.
    admin_approval_status: Mapped[str] = mapped_column(String(30), default="Draft")
    admin_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    vendor_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewed_by_admin_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    history: Mapped[list["VendorOnboardingStatusHistory"]] = relationship(
        "VendorOnboardingStatusHistory", back_populates="status", order_by="VendorOnboardingStatusHistory.changed_at"
    )


class VendorOnboardingStatusHistory(Base):
    """Immutable audit trail (HLD/LLD #10.3) — append-only, no update/delete path exposed."""

    __tablename__ = "vendor_onboarding_status_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vendor_onboarding_status_id: Mapped[int] = mapped_column(ForeignKey("vendor_onboarding_status.vendor_id"))
    vendor_id: Mapped[int] = mapped_column(Integer, index=True)
    from_status: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    to_status: Mapped[str] = mapped_column(String(30))
    action: Mapped[str] = mapped_column(Text)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    changed_by: Mapped[int] = mapped_column(Integer)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    status: Mapped["VendorOnboardingStatus"] = relationship("VendorOnboardingStatus", back_populates="history")


class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[str] = mapped_column(String(4000), nullable=False)  # JSON-encoded
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
