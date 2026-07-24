"""
Global exception handlers for OpportunityOS.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.response import error_response

logger = logging.getLogger(__name__)


class OpportunityOSError(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(OpportunityOSError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class UnauthorizedError(OpportunityOSError):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class ForbiddenError(OpportunityOSError):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class BadRequestError(OpportunityOSError):
    def __init__(self, message: str = "Bad request"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(OpportunityOSError)
    async def application_exception_handler(
        request: Request,
        exc: OpportunityOSError,
    ):
        logger.warning("%s", exc.message)

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(exc.message).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        logger.warning("Validation Error: %s", exc.errors())

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(
                "Validation failed.",
                details=exc.errors(),
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def internal_exception_handler(
        request: Request,
        exc: Exception,
    ):
        logger.exception(exc)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(
                "Internal server error."
            ).model_dump(),
        )