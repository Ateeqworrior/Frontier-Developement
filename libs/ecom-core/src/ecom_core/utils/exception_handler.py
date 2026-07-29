from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .errors import (
    AccountBlockedError,
    CarsAuthFailedError,
    DatabaseException,
    DuplicateResourceError,
    InvalidCredentialsError,
    InvalidPriceRangeError,
    InvalidSearchQueryError,
    ProductNotFoundError,
    UdidNotMatchedError,
    UdidServiceUnavailableError,
)
from .standard_response import StandardResponse

_STATUS_BY_EXC = {
    AccountBlockedError: status.HTTP_403_FORBIDDEN,
    InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
    CarsAuthFailedError: status.HTTP_401_UNAUTHORIZED,
    DuplicateResourceError: status.HTTP_409_CONFLICT,
    UdidNotMatchedError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    UdidServiceUnavailableError: status.HTTP_502_BAD_GATEWAY,
    DatabaseException: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ProductNotFoundError: status.HTTP_404_NOT_FOUND,
    InvalidPriceRangeError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    InvalidSearchQueryError: status.HTTP_422_UNPROCESSABLE_ENTITY,
}


def register_exception_handlers(app) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=StandardResponse.fail("validation error", "validation_error", str(exc.errors())).model_dump(),
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=422,
            content=StandardResponse.fail("validation error", "validation_error", str(exc)).model_dump(),
        )

    for exc_type, http_code in _STATUS_BY_EXC.items():
        def _make_handler(code: int):
            async def _handler(request: Request, exc: Exception):
                return JSONResponse(
                    status_code=code,
                    content=StandardResponse.fail(
                        str(exc), getattr(exc, "message_code", "error")
                    ).model_dump(),
                )

            return _handler

        app.add_exception_handler(exc_type, _make_handler(http_code))

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=StandardResponse.fail("internal server error", "internal_error", str(exc)).model_dump(),
        )
