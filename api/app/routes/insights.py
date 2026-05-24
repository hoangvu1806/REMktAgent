from uuid import uuid4

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.models.insight import (
    InsightCollectionRequest,
    MarketInsightSnapshot,
    UpdateAssumptionsRequest,
)
from app.models.responses import ApiResponse, ErrorResponse
from app.services.insight_service import InsightNotFoundError, InsightService
from app.services.project_service import ProjectNotFoundError


router = APIRouter(prefix="/projects/{project_id}/insights", tags=["insights"])


@router.post(
    "",
    response_model=ApiResponse[MarketInsightSnapshot],
    status_code=status.HTTP_201_CREATED,
)
def collect_insights(
    project_id: str, payload: InsightCollectionRequest
) -> ApiResponse[MarketInsightSnapshot] | JSONResponse:
    service = InsightService()
    try:
        snapshot = service.collect_snapshot(project_id, payload)
    except ProjectNotFoundError:
        return _not_found("Project was not found.", {"project_id": project_id})
    return ApiResponse(data=snapshot, meta={"correlation_id": _correlation_id()})


@router.get("", response_model=ApiResponse[list[MarketInsightSnapshot]])
def list_insights(
    project_id: str,
) -> ApiResponse[list[MarketInsightSnapshot]] | JSONResponse:
    service = InsightService()
    try:
        snapshots = service.list_snapshots(project_id)
    except ProjectNotFoundError:
        return _not_found("Project was not found.", {"project_id": project_id})
    return ApiResponse(data=snapshots, meta={"correlation_id": _correlation_id()})


@router.patch(
    "/{snapshot_id}/assumptions",
    response_model=ApiResponse[MarketInsightSnapshot],
)
def update_assumptions(
    project_id: str,
    snapshot_id: str,
    payload: UpdateAssumptionsRequest,
) -> ApiResponse[MarketInsightSnapshot] | JSONResponse:
    service = InsightService()
    try:
        snapshot = service.update_assumptions(project_id, snapshot_id, payload)
    except ProjectNotFoundError:
        return _not_found("Project was not found.", {"project_id": project_id})
    except InsightNotFoundError:
        return _not_found(
            "Market insight snapshot was not found.",
            {"project_id": project_id, "snapshot_id": snapshot_id},
        )
    return ApiResponse(data=snapshot, meta={"correlation_id": _correlation_id()})


def _not_found(message: str, details: dict[str, str]) -> JSONResponse:
    error = ErrorResponse(
        error={
            "code": "not_found",
            "message": message,
            "details": details,
            "recoverable": True,
        },
        meta={"correlation_id": _correlation_id()},
    )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=error.model_dump(),
    )


def _correlation_id() -> str:
    return str(uuid4())
