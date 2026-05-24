import json
import sqlite3
from typing import Any

from app.models.insight import (
    InsightLabel,
    InsightStatus,
    MarketAssumption,
    MarketInsightSnapshot,
    MarketSignal,
)
from app.storage.sqlite import SQLiteStore


class InsightStore(SQLiteStore):
    def save_snapshot(self, snapshot: MarketInsightSnapshot) -> MarketInsightSnapshot:
        with self._connect() as connection:
            self._ensure_schema(connection)
            connection.execute(
                """
                INSERT OR REPLACE INTO market_insight_snapshots (
                    snapshot_id,
                    project_id,
                    status,
                    summary,
                    assumptions,
                    unavailable_signals,
                    confirmed,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot.snapshot_id,
                    snapshot.project_id,
                    snapshot.status.value,
                    snapshot.summary,
                    json.dumps([item.model_dump() for item in snapshot.assumptions]),
                    json.dumps(snapshot.unavailable_signals),
                    int(snapshot.confirmed),
                    snapshot.created_at,
                    snapshot.updated_at,
                ),
            )
            connection.execute(
                "DELETE FROM market_signals WHERE snapshot_id = ?",
                (snapshot.snapshot_id,),
            )
            connection.executemany(
                """
                INSERT INTO market_signals (
                    signal_id,
                    snapshot_id,
                    signal_type,
                    label,
                    summary,
                    source_id,
                    source_title,
                    source_url,
                    confidence
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        signal.signal_id,
                        snapshot.snapshot_id,
                        signal.signal_type,
                        signal.label.value,
                        signal.summary,
                        signal.source_id,
                        signal.source_title,
                        signal.source_url,
                        signal.confidence,
                    )
                    for signal in snapshot.signals
                ],
            )
        return snapshot

    def list_snapshots(self, project_id: str) -> list[MarketInsightSnapshot]:
        with self._connect() as connection:
            self._ensure_schema(connection)
            rows = connection.execute(
                """
                SELECT *
                FROM market_insight_snapshots
                WHERE project_id = ?
                ORDER BY created_at ASC
                """,
                (project_id,),
            ).fetchall()
            signals_by_snapshot = {
                row["snapshot_id"]: self._signals_for_snapshot(
                    connection, row["snapshot_id"]
                )
                for row in rows
            }
        return [
            self._row_to_snapshot(row, signals_by_snapshot[row["snapshot_id"]])
            for row in rows
        ]

    def get_snapshot(
        self, project_id: str, snapshot_id: str
    ) -> MarketInsightSnapshot | None:
        with self._connect() as connection:
            self._ensure_schema(connection)
            row = connection.execute(
                """
                SELECT *
                FROM market_insight_snapshots
                WHERE project_id = ? AND snapshot_id = ?
                """,
                (project_id, snapshot_id),
            ).fetchone()
            if row is None:
                return None
            signals = self._signals_for_snapshot(connection, snapshot_id)
        return self._row_to_snapshot(row, signals)

    def _signals_for_snapshot(
        self, connection: sqlite3.Connection, snapshot_id: str
    ) -> list[MarketSignal]:
        rows = connection.execute(
            """
            SELECT *
            FROM market_signals
            WHERE snapshot_id = ?
            ORDER BY rowid ASC
            """,
            (snapshot_id,),
        ).fetchall()
        return [self._row_to_signal(row) for row in rows]

    def _ensure_schema(self, connection: sqlite3.Connection) -> None:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS market_insight_snapshots (
                snapshot_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                status TEXT NOT NULL,
                summary TEXT NOT NULL,
                assumptions TEXT NOT NULL,
                unavailable_signals TEXT NOT NULL,
                confirmed INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS market_signals (
                signal_id TEXT PRIMARY KEY,
                snapshot_id TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                label TEXT NOT NULL,
                summary TEXT NOT NULL,
                source_id TEXT,
                source_title TEXT,
                source_url TEXT,
                confidence TEXT NOT NULL,
                FOREIGN KEY(snapshot_id) REFERENCES market_insight_snapshots(snapshot_id)
            )
            """
        )

    def _row_to_snapshot(
        self, row: sqlite3.Row, signals: list[MarketSignal]
    ) -> MarketInsightSnapshot:
        values: dict[str, Any] = dict(row)
        return MarketInsightSnapshot(
            snapshot_id=values["snapshot_id"],
            project_id=values["project_id"],
            status=InsightStatus(values["status"]),
            summary=values["summary"],
            signals=signals,
            assumptions=[
                MarketAssumption(**item)
                for item in json.loads(values["assumptions"])
            ],
            unavailable_signals=json.loads(values["unavailable_signals"]),
            confirmed=bool(values["confirmed"]),
            created_at=values["created_at"],
            updated_at=values["updated_at"],
        )

    def _row_to_signal(self, row: sqlite3.Row) -> MarketSignal:
        values: dict[str, Any] = dict(row)
        return MarketSignal(
            signal_id=values["signal_id"],
            signal_type=values["signal_type"],
            label=InsightLabel(values["label"]),
            summary=values["summary"],
            source_id=values["source_id"],
            source_title=values["source_title"],
            source_url=values["source_url"],
            confidence=values["confidence"],
        )
