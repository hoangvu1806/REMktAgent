import json
import sqlite3
from typing import Any

from app.models.project import Project, ProjectBrief, ProjectBriefCreate
from app.storage.sqlite import SQLiteStore


class ProjectStore(SQLiteStore):
    def save_project(
        self,
        *,
        project_id: str,
        payload: ProjectBriefCreate,
        created_at: str,
        updated_at: str,
    ) -> Project:
        with self._connect() as connection:
            self._ensure_schema(connection)
            connection.execute(
                """
                INSERT INTO projects (project_id, project_name, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (project_id, payload.project_name, created_at, updated_at),
            )
            connection.execute(
                """
                INSERT INTO project_briefs (
                    project_id,
                    property_segment,
                    location,
                    price_range,
                    key_selling_points,
                    campaign_objective,
                    buyer_profile,
                    tone,
                    promotion_details
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    payload.property_segment.value,
                    payload.location,
                    payload.price_range,
                    json.dumps(payload.key_selling_points),
                    payload.campaign_objective,
                    payload.buyer_profile,
                    payload.tone,
                    payload.promotion_details,
                ),
            )

        return Project(
            project_id=project_id,
            project_name=payload.project_name,
            brief=ProjectBrief(
                property_segment=payload.property_segment,
                location=payload.location,
                price_range=payload.price_range,
                key_selling_points=payload.key_selling_points,
                campaign_objective=payload.campaign_objective,
                buyer_profile=payload.buyer_profile,
                tone=payload.tone,
                promotion_details=payload.promotion_details,
            ),
            created_at=created_at,
            updated_at=updated_at,
        )

    def get_project(self, project_id: str) -> Project | None:
        with self._connect() as connection:
            self._ensure_schema(connection)
            row = connection.execute(
                """
                SELECT
                    p.project_id,
                    p.project_name,
                    p.created_at,
                    p.updated_at,
                    b.property_segment,
                    b.location,
                    b.price_range,
                    b.key_selling_points,
                    b.campaign_objective,
                    b.buyer_profile,
                    b.tone,
                    b.promotion_details
                FROM projects p
                JOIN project_briefs b ON b.project_id = p.project_id
                WHERE p.project_id = ?
                """,
                (project_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_project(row)

    def update_project(
        self,
        *,
        project_id: str,
        payload: ProjectBriefCreate,
        updated_at: str,
    ) -> Project | None:
        with self._connect() as connection:
            self._ensure_schema(connection)
            existing = connection.execute(
                "SELECT created_at FROM projects WHERE project_id = ?",
                (project_id,),
            ).fetchone()
            if existing is None:
                return None

            connection.execute(
                """
                UPDATE projects
                SET project_name = ?, updated_at = ?
                WHERE project_id = ?
                """,
                (payload.project_name, updated_at, project_id),
            )
            connection.execute(
                """
                UPDATE project_briefs
                SET
                    property_segment = ?,
                    location = ?,
                    price_range = ?,
                    key_selling_points = ?,
                    campaign_objective = ?,
                    buyer_profile = ?,
                    tone = ?,
                    promotion_details = ?
                WHERE project_id = ?
                """,
                (
                    payload.property_segment.value,
                    payload.location,
                    payload.price_range,
                    json.dumps(payload.key_selling_points),
                    payload.campaign_objective,
                    payload.buyer_profile,
                    payload.tone,
                    payload.promotion_details,
                    project_id,
                ),
            )

        return self.get_project(project_id)

    def _ensure_schema(self, connection: sqlite3.Connection) -> None:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY,
                project_name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS project_briefs (
                project_id TEXT PRIMARY KEY,
                property_segment TEXT NOT NULL,
                location TEXT NOT NULL,
                price_range TEXT NOT NULL,
                key_selling_points TEXT NOT NULL,
                campaign_objective TEXT NOT NULL,
                buyer_profile TEXT NOT NULL,
                tone TEXT NOT NULL,
                promotion_details TEXT,
                FOREIGN KEY(project_id) REFERENCES projects(project_id)
            )
            """
        )

    def _row_to_project(self, row: sqlite3.Row) -> Project:
        values: dict[str, Any] = dict(row)
        return Project(
            project_id=values["project_id"],
            project_name=values["project_name"],
            created_at=values["created_at"],
            updated_at=values["updated_at"],
            brief=ProjectBrief(
                property_segment=values["property_segment"],
                location=values["location"],
                price_range=values["price_range"],
                key_selling_points=json.loads(values["key_selling_points"]),
                campaign_objective=values["campaign_objective"],
                buyer_profile=values["buyer_profile"],
                tone=values["tone"],
                promotion_details=values["promotion_details"],
            ),
        )
