from typing import Any, Generic, TypeVar

from pydantic import BaseModel


DataT = TypeVar("DataT")


class ResponseMeta(BaseModel):
    correlation_id: str


class ApiResponse(BaseModel, Generic[DataT]):
    data: DataT
    meta: ResponseMeta


class ErrorBody(BaseModel):
    code: str
    message: str
    details: dict[str, Any]
    recoverable: bool


class ErrorResponse(BaseModel):
    error: ErrorBody
    meta: ResponseMeta
