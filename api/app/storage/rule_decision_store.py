import json
import sqlite3
from typing import Any

from app.models.rules import RuleDecisionRecord
from app.storage.sqlite import SQLiteStore


class RuleDecisionStore(SQLiteStore):
    def save(self, record: RuleDecisionRecord) -> RuleDecisionRecord:
        with self._connect() as connection:
            self._ensure_schema(connection)
            connection.execute(
                """
                INSERT OR REPLACE INTO rule_decision_records (
                    rule_decision_id,
                    project_id,
                    decision_type,
                    rule_version,
                    input_json,
                    output_json,
                    timestamp
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.rule_decision_id,
                    record.project_id,
                    record.decision_type,
                    record.rule_version,
                    json.dumps(record.input),
                    json.dumps(record.output),
                    record.timestamp,
                ),
            )
        return record

    def list_by_project(self, project_id: str) -> list[RuleDecisionRecord]:
        with self._connect() as connection:
            self._ensure_schema(connection)
            rows = connection.execute(
                """
                SELECT *
                FROM rule_decision_records
                WHERE project_id = ?
                ORDER BY timestamp ASC, rowid ASC
                """,
                (project_id,),
            ).fetchall()
        return [self._row_to_record(row) for row in rows]

    def _ensure_schema(self, connection: sqlite3.Connection) -> None:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS rule_decision_records (
                rule_decision_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                decision_type TEXT NOT NULL,
                rule_version TEXT NOT NULL,
                input_json TEXT NOT NULL,
                output_json TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )

    def _row_to_record(self, row: sqlite3.Row) -> RuleDecisionRecord:
        values: dict[str, Any] = dict(row)
        return RuleDecisionRecord(
            rule_decision_id=values["rule_decision_id"],
            project_id=values["project_id"],
            decision_type=values["decision_type"],
            rule_version=values["rule_version"],
            input=json.loads(values["input_json"]),
            output=json.loads(values["output_json"]),
            timestamp=values["timestamp"],
        )
