from uuid import uuid4

from fastapi import status
from fastapi.responses import JSONResponse

from app.models.responses import ErrorResponse


def correlation_id() -> str:
    return str(uuid4())


def not_found(message: str, details: dict[str, str]) -> JSONResponse:
    return _error(
        status.HTTP_404_NOT_FOUND,
        "not_found",
        message,
        details,
    )


def source_unavailable(message: str, details: dict[str, str]) -> JSONResponse:
    return _error(
        status.HTTP_502_BAD_GATEWAY,
        "source_unavailable",
        message,
        details,
    )


def _error(
    status_code: int,
    code: str,
    message: str,
    details: dict[str, str],
) -> JSONResponse:
    error = ErrorResponse(
        error={
            "code": code,
            "message": message,
            "details": details,
            "recoverable": True,
        },
        meta={"correlation_id": correlation_id()},
    )
    return JSONResponse(status_code=status_code, content=error.model_dump())
