"""Transactional local state, separate from immutable imported YAML archives."""

from contextlib import closing, contextmanager
from dataclasses import dataclass
import json
import hashlib
import os
from pathlib import Path
import sqlite3
import time
from typing import Any, Iterator
from uuid import uuid4

from src.utils.config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS workouts (
    id TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    document TEXT NOT NULL,
    deleted INTEGER NOT NULL DEFAULT 0,
    version INTEGER NOT NULL CHECK (version > 0)
);
CREATE INDEX IF NOT EXISTS workouts_date ON workouts(date);
CREATE TABLE IF NOT EXISTS measurements (
    date TEXT PRIMARY KEY,
    document TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
    token_hash TEXT PRIMARY KEY,
    csrf_token TEXT NOT NULL,
    expires INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS configuration (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS login_attempts (
    client TEXT PRIMARY KEY,
    started INTEGER NOT NULL,
    attempts INTEGER NOT NULL
);
"""
MIGRATIONS = (SCHEMA, """
ALTER TABLE workouts ADD COLUMN creation_key TEXT;
ALTER TABLE workouts ADD COLUMN request_hash TEXT;
CREATE UNIQUE INDEX workouts_creation_key ON workouts(creation_key) WHERE creation_key IS NOT NULL;
""")
SCHEMA_VERSION = len(MIGRATIONS)


def _schema_version(connection: sqlite3.Connection) -> int:
    version = int(connection.execute("PRAGMA user_version").fetchone()[0])
    if version > SCHEMA_VERSION:
        raise sqlite3.DatabaseError("State schema is newer than this application supports")
    return version


def _migrate(connection: sqlite3.Connection) -> None:
    version = _schema_version(connection)
    for target, migration in enumerate(MIGRATIONS[version:], start=version + 1):
        statement = ""
        for line in migration.splitlines(keepends=True):
            statement += line
            if sqlite3.complete_statement(statement):
                connection.execute(statement)
                statement = ""
        if statement.strip():
            raise sqlite3.DatabaseError("Incomplete state schema migration")
        connection.execute(f"PRAGMA user_version = {target}")


class VersionConflict(ValueError):
    pass


@dataclass(frozen=True)
class StateSnapshot:
    workouts: list[dict[str, Any]]
    measurements: list[dict[str, Any]]
    configuration: dict[str, str]


def _decode_workouts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [{"record": json.loads(row["document"]), "deleted": bool(row["deleted"]), "version": row["version"]} for row in rows]


class StateStore:
    def __init__(self, path: Path | None = None) -> None:
        self._path = path

    @property
    def path(self) -> Path:
        if self._path is not None:
            return self._path.expanduser()
        directory = settings.get("STATE_DIR") or str(Path(settings.DATA_DIR) / ".state")
        return Path(str(directory)).expanduser() / "tracker.sqlite3"

    @contextmanager
    def connection(self, *, write: bool = False) -> Iterator[sqlite3.Connection]:
        if write:
            self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        connection = sqlite3.connect(self.path, timeout=10)
        try:
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA busy_timeout=10000")
            _schema_version(connection)
            if write:
                self.path.chmod(0o600)
                connection.execute("BEGIN IMMEDIATE")
                _migrate(connection)
            yield connection
            if write:
                connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def migrate(self) -> None:
        with self.connection(write=True):
            pass

    def backup(self, destination: Path, *, timeout: float = 30) -> None:
        destination = destination.expanduser()
        if destination.resolve() == self.path.resolve():
            raise ValueError("A backup must not replace the live database")
        if not 0 < timeout <= 3600:
            raise ValueError("Backup timeout must be between zero and 3600 seconds")
        destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.close(os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600))
        deadline = time.monotonic() + timeout

        def progress(status: int, remaining: int, total: int) -> None:
            if time.monotonic() >= deadline:
                raise TimeoutError("Timed out creating a consistent state backup")

        try:
            with closing(sqlite3.connect(destination, timeout=10)) as target:
                if self.path.is_file():
                    with self.connection() as source:
                        source.backup(target, pages=128, progress=progress, sleep=0.05)
                target.execute("PRAGMA journal_mode=DELETE")
                if target.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                    raise sqlite3.DatabaseError("State backup failed its integrity check")
            StateStore(destination).migrate()
        except Exception:
            destination.unlink(missing_ok=True)
            raise

    def read(self, query: str, parameters: tuple = ()) -> list[sqlite3.Row]:
        if not self.path.is_file():
            return []
        with self.connection() as connection:
            return connection.execute(query, parameters).fetchall()

    def workout_rows(self) -> list[dict[str, Any]]:
        return _decode_workouts(self.read("SELECT document, deleted, version FROM workouts ORDER BY date, id"))

    def snapshot(self) -> StateSnapshot:
        if not self.path.is_file():
            return StateSnapshot([], [], {})
        with self.connection() as connection:
            connection.execute("BEGIN")
            workouts = _decode_workouts(connection.execute("SELECT document, deleted, version FROM workouts ORDER BY date, id").fetchall())
            measurements = [json.loads(row["document"]) for row in connection.execute("SELECT document FROM measurements ORDER BY date")]
            configuration = {str(row["key"]): str(row["value"]) for row in connection.execute("SELECT key, value FROM configuration WHERE key LIKE 'program:%'")}
        return StateSnapshot(workouts, measurements, configuration)

    def workout(self, identifier: str) -> dict[str, Any] | None:
        rows = self.read("SELECT document, deleted, version FROM workouts WHERE id = ?", (identifier,))
        return {"record": json.loads(rows[0]["document"]), "deleted": bool(rows[0]["deleted"]), "version": rows[0]["version"]} if rows else None

    def create_workout(self, payload: dict[str, Any], *, idempotency_key: str | None = None) -> dict[str, Any]:
        fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
        with self.connection(write=True) as connection:
            if idempotency_key is not None:
                existing = connection.execute("SELECT document, version, deleted, request_hash FROM workouts WHERE creation_key = ?", (idempotency_key,)).fetchone()
                if existing:
                    if existing["request_hash"] != fingerprint:
                        raise VersionConflict("This creation key was already used with different workout data; reload before saving")
                    if existing["deleted"] or existing["version"] != 1:
                        raise VersionConflict("The original workout was changed or deleted; reload before saving")
                    return dict(json.loads(existing["document"]))
            record = {**payload, "id": self.new_id()}
            connection.execute(
                "INSERT INTO workouts(id, date, document, deleted, version, creation_key, request_hash) VALUES (?, ?, ?, 0, 1, ?, ?)",
                (record["id"], record["date"], json.dumps(record, allow_nan=False), idempotency_key, fingerprint if idempotency_key is not None else None),
            )
        return record

    def save_workout(self, record: dict[str, Any], *, expected_version: int | None = None, deleted: bool = False) -> int:
        identifier = str(record["id"])
        with self.connection(write=True) as connection:
            existing = connection.execute("SELECT version, deleted FROM workouts WHERE id = ?", (identifier,)).fetchone()
            current_version = existing["version"] if existing else 1
            if expected_version is not None and (expected_version != current_version or (existing and existing["deleted"])):
                raise VersionConflict("This workout changed; reload it before saving")
            if expected_version is None and existing:
                raise VersionConflict("Workout ID already exists")
            version = current_version + 1 if expected_version is not None else 1
            connection.execute(
                "INSERT INTO workouts(id, date, document, deleted, version) VALUES (?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET date=excluded.date, document=excluded.document, deleted=excluded.deleted, version=excluded.version",
                (identifier, record["date"], json.dumps(record, allow_nan=False), int(deleted), version),
            )
        return version

    def measurements(self) -> list[dict[str, Any]]:
        return [json.loads(row["document"]) for row in self.read("SELECT document FROM measurements ORDER BY date")]

    def save_measurements(self, measurements: list[dict[str, Any]]) -> None:
        with self.connection(write=True) as connection:
            for measurement in measurements:
                previous = connection.execute("SELECT document FROM measurements WHERE date = ?", (measurement["date"],)).fetchone()
                updated = {**(json.loads(previous["document"]) if previous else {}), **measurement}
                connection.execute(
                    "INSERT INTO measurements(date, document) VALUES (?, ?) ON CONFLICT(date) DO UPDATE SET document=excluded.document",
                    (measurement["date"], json.dumps(updated, allow_nan=False)),
                )

    def import_workouts(self, records: list[dict[str, Any]]) -> None:
        with self.connection(write=True) as connection:
            for record in records:
                connection.execute("INSERT INTO workouts(id, date, document, deleted, version) VALUES (?, ?, ?, 0, 1)", (record["id"], record["date"], json.dumps(record, allow_nan=False)))

    def delete_measurement(self, measured_date: str) -> bool:
        with self.connection(write=True) as connection:
            return connection.execute("DELETE FROM measurements WHERE date = ?", (measured_date,)).rowcount > 0

    def configuration(self, key: str) -> str | None:
        rows = self.read("SELECT value FROM configuration WHERE key = ?", (key,))
        return str(rows[0]["value"]) if rows else None

    def configure(self, key: str, value: str) -> None:
        with self.connection(write=True) as connection:
            connection.execute("INSERT INTO configuration(key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))
            if key == "password_hash":
                connection.execute("DELETE FROM sessions")

    def session(self, token_hash: str, now: int) -> dict[str, Any] | None:
        rows = self.read("SELECT csrf_token, expires FROM sessions WHERE token_hash = ? AND expires > ?", (token_hash, now))
        return dict(rows[0]) if rows else None

    def create_session(self, token_hash: str, csrf_token: str, expires: int, now: int) -> None:
        with self.connection(write=True) as connection:
            connection.execute("DELETE FROM sessions WHERE expires <= ?", (now,))
            connection.execute("INSERT INTO sessions(token_hash, csrf_token, expires) VALUES (?, ?, ?)", (token_hash, csrf_token, expires))

    def revoke_session(self, token_hash: str) -> None:
        with self.connection(write=True) as connection:
            connection.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash,))

    def allow_login(self, client: str, now: int) -> bool:
        with self.connection(write=True) as connection:
            connection.execute("DELETE FROM login_attempts WHERE started < ?", (now - 900,))
            row = connection.execute("SELECT started, attempts FROM login_attempts WHERE client = ?", (client,)).fetchone()
            if row and row["attempts"] >= 10:
                return False
            connection.execute("INSERT INTO login_attempts(client, started, attempts) VALUES (?, ?, 1) ON CONFLICT(client) DO UPDATE SET attempts=attempts+1", (client, now))
        return True

    def new_id(self) -> str:
        return str(uuid4())


state_store = StateStore()