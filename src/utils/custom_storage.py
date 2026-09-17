"""Extend TinyDB with locked, atomic YAML storage."""

import os
from pathlib import Path
import stat
from tempfile import NamedTemporaryFile
from threading import Lock, RLock
from typing import Any
from uuid import UUID, uuid4

from pydantic import ValidationError
from tinydb.storages import Storage  # type: ignore
import yaml  # type: ignore

from src.common.workout_types import (
    WorkoutData,
    is_workout_record,
    legacy_workout_id,
    parse_workout_date,
)


class YAMLStorage(Storage):
    """YAML storage that avoids partial writes within one application process."""

    _locks: dict[Path, RLock] = {}
    _locks_guard = Lock()

    def __init__(
        self,
        filename: str | Path,
        *,
        workout_table: str | None = None,
        workout_year: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__()
        self.kwargs = kwargs
        self.workout_table = workout_table
        self.workout_year = workout_year
        self.filename = Path(filename).expanduser().resolve()
        self.filename.parent.mkdir(parents=True, exist_ok=True)
        if not self.filename.exists():
            self.filename.touch()
        with self._locks_guard:
            self._lock = self._locks.setdefault(self.filename, RLock())

    def read(self) -> dict[str, Any] | None:
        with self._lock, self.filename.open(encoding="utf-8") as handle:
            return yaml.safe_load(handle)

    def write(self, data: dict[str, Any]) -> None:
        temporary_path: Path | None = None
        with self._lock:
            if self.workout_table is not None:
                data = self._with_workout_ids(data, self.read() or {})
            try:
                existing_mode = stat.S_IMODE(self.filename.stat().st_mode)
                with NamedTemporaryFile(
                    mode="w",
                    encoding="utf-8",
                    dir=self.filename.parent,
                    prefix=f".{self.filename.name}.",
                    suffix=".tmp",
                    delete=False,
                ) as handle:
                    temporary_path = Path(handle.name)
                    yaml.safe_dump(data, handle, sort_keys=False)
                    handle.flush()
                    os.fsync(handle.fileno())
                temporary_path.chmod(existing_mode)
                os.replace(temporary_path, self.filename)
            finally:
                if temporary_path is not None and temporary_path.exists():
                    temporary_path.unlink()

    def _with_workout_ids(
        self, data: dict[str, Any], previous: dict[str, Any]
    ) -> dict[str, Any]:
        if self.workout_table is None or self.workout_table not in data:
            return data
        previous_records = previous.get(self.workout_table, {})
        records = {}
        seen_ids: set[UUID] = set()
        for document_id, record in data[self.workout_table].items():
            previous_record = previous_records.get(document_id, {})
            if not isinstance(record, dict) or "date" not in record:
                records[document_id] = record
                continue
            try:
                WorkoutData.model_validate(record)
            except ValidationError as exc:
                if record == previous_record:
                    records[document_id] = record
                    continue
                raise ValueError(f"Invalid workout document {document_id}: {exc}") from exc
            supplied_id = record.get("id")
            if is_workout_record(previous_record):
                year = self.workout_year or parse_workout_date(previous_record["date"]).year
                previous_id = previous_record.get("id")
                workout_id = (
                    UUID(str(previous_id))
                    if previous_id
                    else legacy_workout_id(year, int(document_id))
                )
                if supplied_id is not None and UUID(str(supplied_id)) != workout_id:
                    raise ValueError("Workout IDs are immutable")
            else:
                workout_id = UUID(str(supplied_id)) if supplied_id else uuid4()
            if workout_id in seen_ids:
                raise ValueError(f"Duplicate workout ID: {workout_id}")
            seen_ids.add(workout_id)
            records[document_id] = {**record, "id": str(workout_id)}
        return {**data, self.workout_table: records}

    def migrate_workout_ids(self, *, dry_run: bool = False) -> int:
        """Backfill existing IDs without changing the URLs of legacy records."""
        if self.workout_table is None:
            raise ValueError("A workout table is required to migrate IDs")
        with self._lock:
            data = self.read() or {}
            updated = self._with_workout_ids(data, data)
            count = sum(
                record != data[self.workout_table][document_id]
                for document_id, record in updated.get(self.workout_table, {}).items()
            )
            if count and not dry_run:
                self.write(updated)
            return count

    def close(self) -> None:
        pass
