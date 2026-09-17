"""File-versioned workout snapshots and a persistent-ID lookup index."""

from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from typing import Any
from uuid import UUID

from loguru import logger
from pydantic import ValidationError

from src.common.workout_types import WorkoutData, get_workout_id
from src.utils.config import settings
from src.utils.set_db_and_table import get_available_years, get_database_path, set_db_and_table

WorkoutDocument = tuple[int, dict[str, Any]]
SnapshotKey = tuple[int, Path, str]
FileVersion = tuple[int, int, int, int, int]


def _file_version(path: Path) -> FileVersion:
    metadata = path.stat()
    return (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_size,
        metadata.st_mtime_ns,
        metadata.st_ctime_ns,
    )


@dataclass(frozen=True)
class WorkoutSnapshot:
    version: FileVersion
    documents: tuple[WorkoutDocument, ...]
    by_id: dict[UUID, WorkoutDocument]


class WorkoutRepository:
    """Cache validated records until their backing file changes."""

    def __init__(self) -> None:
        self._snapshots: dict[SnapshotKey, WorkoutSnapshot] = {}
        self._index: dict[UUID, SnapshotKey] = {}
        self._lock = RLock()

    def clear(self) -> None:
        with self._lock:
            self._snapshots.clear()
            self._index.clear()

    def _remove(self, key: SnapshotKey) -> None:
        snapshot = self._snapshots.pop(key)
        for workout_id in snapshot.by_id:
            self._index.pop(workout_id, None)

    def _available_keys(self) -> dict[int, SnapshotKey]:
        table_name = str(settings.REAL_WEIGHT_TABLE)
        keys = {
            year: (year, get_database_path("real", year=year).resolve(), table_name)
            for year in get_available_years()
        }
        active = set(keys.values())
        for key in tuple(self._snapshots):
            if key not in active or self._snapshots[key].version != _file_version(key[1]):
                self._remove(key)
        return keys

    def _load(self, key: SnapshotKey) -> WorkoutSnapshot:
        year, path, _ = key
        version = _file_version(path)
        cached = self._snapshots.get(key)
        if cached is not None and cached.version == version:
            return cached

        for _ in range(3):
            _, table, _ = set_db_and_table("real", year=year, create=False)
            documents: list[WorkoutDocument] = []
            for item in table:
                try:
                    validated_record = WorkoutData.model_validate(item)
                except ValidationError as exc:
                    logger.warning(
                        "Skipping invalid workout document {} in {}: {}",
                        item.doc_id,
                        year,
                        [error["loc"] for error in exc.errors()],
                    )
                    continue
                documents.append(
                    (item.doc_id, validated_record.model_dump(mode="json", exclude_unset=True))
                )
            after_read = _file_version(path)
            if after_read == version:
                break
            version = after_read
        else:
            raise OSError("Workout database changed repeatedly while reading")

        documents.sort(key=lambda document: (document[1]["date"], document[0]))
        by_id: dict[UUID, WorkoutDocument] = {}
        for document_id, record in documents:
            workout_id = get_workout_id(record, year, document_id)
            if workout_id in by_id or self._index.get(workout_id, key) != key:
                raise ValueError(f"Duplicate workout ID: {workout_id}")
            by_id[workout_id] = (document_id, record)

        snapshot = WorkoutSnapshot(version, tuple(documents), by_id)
        if cached is not None:
            self._remove(key)
        self._snapshots[key] = snapshot
        self._index.update(dict.fromkeys(by_id, key))
        return snapshot

    def documents(self, year: int, *, descending: bool = False) -> list[WorkoutDocument]:
        with self._lock:
            keys = self._available_keys()
            if year not in keys:
                raise FileNotFoundError(f"No workout data for {year}")
            snapshot = self._load(keys[year])
            return list(reversed(snapshot.documents) if descending else snapshot.documents)

    def find(self, workout_id: UUID) -> tuple[int, int, dict[str, Any]] | None:
        with self._lock:
            keys = self._available_keys()
            if workout_id not in self._index:
                for key in reversed(tuple(keys.values())):
                    if workout_id in self._load(key).by_id:
                        break
            matching_key = self._index.get(workout_id)
            if matching_key is None:
                return None
            document_id, record = self._snapshots[matching_key].by_id[workout_id]
            return matching_key[0], document_id, record