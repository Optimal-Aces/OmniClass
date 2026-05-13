import sqlite3
import logging
from app.config import DB_PATH, DB_VERSION

logger = logging.getLogger(__name__)

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._conn = None
        return cls._instance

    def connect(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(
                str(DB_PATH),
                check_same_thread=False,
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON")
            self._conn.execute("PRAGMA journal_mode = WAL")
        return self._conn

    def initialize(self):
        conn = self.connect()
        current = self._get_version(conn)
        if current < DB_VERSION:
            self._run_migrations(conn, current)
        logger.info(f"Database ready — v{DB_VERSION}")

    def _get_version(self, conn) -> int:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS _schema_version (version INTEGER NOT NULL)"
        )
        row = conn.execute("SELECT version FROM _schema_version").fetchone()
        return row["version"] if row else 0

    def _run_migrations(self, conn, from_version: int):
        from app.core.dao.migrations import MIGRATIONS
        for version, sql in MIGRATIONS.items():
            if version > from_version:
                conn.executescript(sql)
                conn.execute("DELETE FROM _schema_version")
                conn.execute("INSERT INTO _schema_version VALUES (?)", (version,))
                conn.commit()
                logger.info(f"Migration v{version} applied")

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None