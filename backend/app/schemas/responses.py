"""Standard API response schemas."""

from typing import Any, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str
    field: str | None = None


class Meta(BaseModel):
    request_id: str | None = None


class APIResponse(BaseModel, Generic[T]):
    data: T | None = None
    meta: Meta = Meta()
    errors: list[ErrorDetail] = []
