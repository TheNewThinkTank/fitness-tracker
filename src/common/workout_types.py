"""Shared workout typing helpers for the fitness tracker domain."""

from __future__ import annotations

from datetime import date as calendar_date
from typing import Any
from uuid import UUID, uuid5

from pydantic import BaseModel, ConfigDict, ValidationError, field_validator
from typing_extensions import TypedDict

WORKOUT_ID_NAMESPACE = UUID("580bcb0f-5d7c-4ba7-970f-5ee56fd5f435")


def legacy_workout_id(year: int, document_id: int) -> UUID:
    """Keep existing API links valid while legacy records receive stored IDs."""
    return uuid5(WORKOUT_ID_NAMESPACE, f"{year}:{document_id}")


def get_workout_id(record: dict[str, Any], year: int, document_id: int) -> UUID:
    stored_id = record.get("id")
    return UUID(str(stored_id)) if stored_id else legacy_workout_id(year, document_id)


class ExerciseSet(TypedDict, total=False):
    """Represents a single exercise set inside a workout record."""

    set_number: int
    reps: int
    weight: str


class WorkoutRecord(TypedDict):
    """Represents a normalized workout record stored in the database."""

    date: str
    split: str
    exercises: dict[str, list[ExerciseSet]]


def parse_workout_date(value: Any) -> calendar_date:
    """Parse a calendar date without accepting timestamps or compact dates."""
    if type(value) is calendar_date:
        return value
    if isinstance(value, str):
        try:
            parsed_date = calendar_date.fromisoformat(value)
            if parsed_date.isoformat() == value:
                return parsed_date
        except ValueError:
            pass
    raise ValueError("date must use YYYY-MM-DD format and be a valid calendar date")


class ExerciseSetResponse(BaseModel):
    model_config = ConfigDict(extra="allow", strict=True)

    set_number: int
    reps: int
    weight: str
    duration: str | None = None


class WorkoutMetadata(BaseModel):
    model_config = ConfigDict(strict=True)

    date: calendar_date
    split: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    timezone: str | None = None

    @field_validator("date", mode="before")
    @classmethod
    def validate_date(cls, value: Any) -> calendar_date:
        return parse_workout_date(value)


class WorkoutData(WorkoutMetadata):
    """Shared validation for imported records and API-readable workout data."""

    model_config = ConfigDict(extra="allow", strict=True)

    id: UUID | None = None
    exercises: dict[str, list[ExerciseSetResponse]] | None = None

    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, value: Any) -> Any:
        return UUID(value) if isinstance(value, str) else value


def is_workout_record(value: Any) -> bool:
    """Return True when a value looks like a workout record.

    The stored data is not perfectly uniform across the project, so this helper
    accepts records that have a valid date and optional split/exercises fields,
    while still rejecting clearly malformed exercise entries.
    """

    if not isinstance(value, dict):
        return False

    try:
        WorkoutData.model_validate(value)
    except ValidationError:
        return False
    return True
