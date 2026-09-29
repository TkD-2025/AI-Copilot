from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class StandardResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T | None = None
