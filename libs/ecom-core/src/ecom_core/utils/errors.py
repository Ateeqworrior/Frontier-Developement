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
