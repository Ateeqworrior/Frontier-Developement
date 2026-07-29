"""Document upload presigning for US-009 (NFR-02: 1-hour expiry, no public bucket access).

TODO(real S3 integration): replace the stub below with a boto3 S3 client's
generate_presigned_url("put_object", ...) call against settings.s3_presign_base_url's
bucket. Stubbed here since no AWS credentials/bucket are reachable from this
environment — the surrounding service logic does not need to change once wired up.
"""

import uuid

from .config import settings


def presign_upload(vendor_id: int, document_field: str) -> dict:
    s3_key = f"vendor-documents/{vendor_id}/{document_field}/{uuid.uuid4().hex}"
    return {
        "upload_url": f"{settings.s3_presign_base_url}/{s3_key}?X-Dev-Stub-Expiry={settings.s3_presign_expiry_seconds}",
        "s3_key": s3_key,
        "expires_in": settings.s3_presign_expiry_seconds,
    }
