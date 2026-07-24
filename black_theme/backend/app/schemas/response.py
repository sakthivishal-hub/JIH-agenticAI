from datetime import datetime, timezone
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    field: Optional[str] = None
    msg: str


class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    errors: Optional[list[ErrorDetail]] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(from_attributes=True, extra="ignore")


def success_response(message: str, data: Optional[T] = None) -> APIResponse[T]:
    return APIResponse[T](success=True, message=message, data=data)


def error_response(
    message: str,
    errors: Optional[list[ErrorDetail]] = None,
    data: Optional[T] = None,
) -> APIResponse[T]:
    return APIResponse[T](success=False, message=message, data=data, errors=errors)