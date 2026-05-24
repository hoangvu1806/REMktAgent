from datetime import UTC, datetime
from uuid import uuid4

from app.models.project import Project, ProjectBriefCreate
from app.storage.project_store import ProjectStore


class ProjectNotFoundError(Exception):
    pass


class ProjectService:
    def __init__(self, store: ProjectStore | None = None) -> None:
        self.store = store or ProjectStore()

    def create_project(self, payload: ProjectBriefCreate) -> Project:
        now = _utc_now()
        return self.store.save_project(
            project_id=str(uuid4()),
            payload=payload,
            created_at=now,
            updated_at=now,
        )

    def get_project(self, project_id: str) -> Project:
        project = self.store.get_project(project_id)
        if project is None:
            raise ProjectNotFoundError(project_id)
        return project

    def update_project(self, project_id: str, payload: ProjectBriefCreate) -> Project:
        project = self.store.update_project(
            project_id=project_id,
            payload=payload,
            updated_at=_utc_now(),
        )
        if project is None:
            raise ProjectNotFoundError(project_id)
        return project


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
