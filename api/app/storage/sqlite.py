import os
import sqlite3
from pathlib import Path


DEFAULT_DATABASE_PATH = Path("data/content_creator.sqlite3")


class SQLiteStore:
    def __init__(self, database_path: str | None = None) -> None:
        self.database_path = Path(
            database_path
            or os.environ.get("SQLITE_DATABASE_PATH")
            or DEFAULT_DATABASE_PATH
        )

    def _connect(self) -> sqlite3.Connection:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection
