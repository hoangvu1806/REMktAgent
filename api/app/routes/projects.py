from uuid import uuid4

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.models.project import Project, ProjectBriefCreate
from app.models.responses import ApiResponse, ErrorResponse
from app.services.project_service import ProjectNotFoundError, ProjectService


router = APIRouter(prefix="/projects", tags=["projects"])


@router.post(
    "",
    response_model=ApiResponse[Project],
    status_code=status.HTTP_201_CREATED,
)
def create_project(payload: ProjectBriefCreate) -> ApiResponse[Project]:
    service = ProjectService()
    return ApiResponse(
        data=service.create_project(payload),
        meta={"correlation_id": _correlation_id()},
    )


@router.get("/{project_id}", response_model=ApiResponse[Project])
def get_project(project_id: str) -> ApiResponse[Project] | JSONResponse:
    service = ProjectService()
    try:
        project = service.get_project(project_id)
    except ProjectNotFoundError:
        error = ErrorResponse(
            error={
                "code": "not_found",
                "message": "Project was not found.",
                "details": {"project_id": project_id},
                "recoverable": True,
            },
            meta={"correlation_id": _correlation_id()},
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error.model_dump(),
        )

    return ApiResponse(data=project, meta={"correlation_id": _correlation_id()})


@router.put("/{project_id}", response_model=ApiResponse[Project])
def update_project(
    project_id: str, payload: ProjectBriefCreate
) -> ApiResponse[Project] | JSONResponse:
    service = ProjectService()
    try:
        project = service.update_project(project_id, payload)
    except ProjectNotFoundError:
        error = ErrorResponse(
            error={
                "code": "not_found",
                "message": "Project was not found.",
                "details": {"project_id": project_id},
                "recoverable": True,
            },
            meta={"correlation_id": _correlation_id()},
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error.model_dump(),
        )

    return ApiResponse(data=project, meta={"correlation_id": _correlation_id()})


def _correlation_id() -> str:
    return str(uuid4())
