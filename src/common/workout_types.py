"""Shared workout typing helpers for the fitness tracker domain."""

from __future__ import annotations

from typing import Any, TypedDict


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


def is_workout_record(value: Any) -> bool:
    """Return True when a value looks like a workout record.

    The stored data is not perfectly uniform across the project, so this helper
    accepts records that have a valid date and optional split/exercises fields,
    while still rejecting clearly malformed exercise entries.
    """

    if not isinstance(value, dict):
        return False

    if not isinstance(value.get("date"), str):
        return False

    split = value.get("split")
    if split is not None and not isinstance(split, str):
        return False

    exercises = value.get("exercises")
    if exercises is None:
        return True

    if not isinstance(exercises, dict):
        return False

    for exercise_sets in exercises.values():
        if not isinstance(exercise_sets, list):
            return False
        for set_data in exercise_sets:
            if not isinstance(set_data, dict):
                return False
            if not isinstance(set_data.get("set_number"), int):
                return False
            if not isinstance(set_data.get("reps"), int):
                return False
            if not isinstance(set_data.get("weight"), str):
                return False

    return True
