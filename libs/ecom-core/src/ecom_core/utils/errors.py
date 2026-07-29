class DatabaseException(Exception):
    pass


class DuplicateResourceError(Exception):
    def __init__(self, message: str, message_code: str = "duplicate_resource"):
        super().__init__(message)
        self.message_code = message_code


class AccountBlockedError(Exception):
    def __init__(self, message: str = "account blocked"):
        super().__init__(message)
        self.message_code = "account_blocked"


class InvalidCredentialsError(Exception):
    def __init__(self, message: str = "invalid credentials"):
        super().__init__(message)
        self.message_code = "invalid_credentials"


class UdidNotMatchedError(Exception):
    def __init__(self, message: str = "UDID did not match a Sarthak Foundation record"):
        super().__init__(message)
        self.message_code = "udid_not_matched"


class UdidServiceUnavailableError(Exception):
    def __init__(self, message: str = "Sarthak Foundation UDID endpoint unavailable"):
        super().__init__(message)
        self.message_code = "udid_service_unavailable"


class CarsAuthFailedError(Exception):
    def __init__(self, message: str = "CARS authentication failed"):
        super().__init__(message)
        self.message_code = "cars_auth_failed"


class ProductNotFoundError(Exception):
    def __init__(self, message: str = "product not found"):
        super().__init__(message)
        self.message_code = "product_not_found"


class InvalidPriceRangeError(Exception):
    def __init__(self, message: str = "price_min must not exceed price_max"):
        super().__init__(message)
        self.message_code = "invalid_price_range"


class InvalidSearchQueryError(Exception):
    def __init__(self, message: str = "search query is missing or too short"):
        super().__init__(message)
        self.message_code = "invalid_search_query"


class OnboardingVersionConflictError(Exception):
    def __init__(self, message: str = "onboarding record was updated elsewhere"):
        super().__init__(message)
        self.message_code = "onboarding_version_conflict"


class OnboardingValidationError(Exception):
    def __init__(self, message: str = "field validation failed"):
        super().__init__(message)
        self.message_code = "field_validation_failed"


class OnboardingIncompleteError(Exception):
    def __init__(self, message: str = "mandatory fields or documents are missing"):
        super().__init__(message)
        self.message_code = "onboarding_incomplete"


class InvalidDocumentFieldError(Exception):
    def __init__(self, message: str = "document field is not valid for this step"):
        super().__init__(message)
        self.message_code = "invalid_document_field"


class RemarksRequiredError(Exception):
    def __init__(self, message: str = "remarks are required to reject a vendor"):
        super().__init__(message)
        self.message_code = "remarks_required"


class CommentsRequiredError(Exception):
    def __init__(self, message: str = "comments are required to request a correction"):
        super().__init__(message)
        self.message_code = "comments_required"


class OnboardingLockedError(Exception):
    def __init__(self, message: str = "onboarding record is locked for edits"):
        super().__init__(message)
        self.message_code = "onboarding_locked"


class VendorOnboardingNotFoundError(Exception):
    def __init__(self, message: str = "vendor onboarding record not found"):
        super().__init__(message)
        self.message_code = "vendor_onboarding_not_found"


class CartItemNotFoundError(Exception):
    def __init__(self, message: str = "cart item not found"):
        super().__init__(message)
        self.message_code = "cart_item_not_found"


class WishlistItemNotFoundError(Exception):
    def __init__(self, message: str = "wishlist item not found"):
        super().__init__(message)
        self.message_code = "wishlist_item_not_found"


class InvalidPinCodeError(Exception):
    def __init__(self, message: str = "pin_code is missing or malformed"):
        super().__init__(message)
        self.message_code = "invalid_pin_code"
