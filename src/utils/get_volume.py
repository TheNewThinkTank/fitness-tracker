"""
Get the total workout volume of each date in the table.
In the case of multiple workouts on the same day,
the volume is the sum of the volumes of the workouts.
"""

from __future__ import annotations

from pprint import pformat  # type: ignore
from typing import Mapping, TypedDict

from loguru import logger  # type: ignore

from src.common.metrics import parse_load, positive_number
from src.utils.set_db_and_table import set_db_and_table  # type: ignore


class ExerciseSet(TypedDict):
    reps: int
    weight: str


class WorkoutEntry(TypedDict):
    date: str
    exercises: dict[str, list[ExerciseSet]]


def get_weight(
        s: ExerciseSet,
        bodyweight: str,
        Sidea_9012_Olympic_Hex_Bar: str
        ) -> float:
    """Get the weight of the exercise in kg.

    Handles plain weights ("80 kg"), bodyweight forms ("BODYWEIGHT",
    "BODYWEIGHT + 10 kg", "BODYWEIGHT - 5 kg"), barbell references
    ("Sidea_9012_Olympic_Hex_Bar"), and powerband modifiers.

    :param s: Dictionary containing the exercise details
    :type s: dict
    :param bodyweight: Bodyweight of the person in kg as a string
    :type bodyweight: str
    :param Sidea_9012_Olympic_Hex_Bar: Weight of the hex bar in kg as a string
    :type Sidea_9012_Olympic_Hex_Bar: str
    :return: Weight of the exercise in kg
    :rtype: float
    """

    parsed = parse_load(
        s["weight"],
        positive_number(bodyweight),
        {"Sidea_9012_Olympic_Hex_Bar": float(Sidea_9012_Olympic_Hex_Bar)},
    )
    if parsed.total_kg is None:
        raise ValueError(f"Load is unavailable: {parsed.reason}")
    return parsed.total_kg


def get_total_volume(table, bodyweights: Mapping[str, float] | None = None) -> list[tuple[str, float]]:
    """Get the total volume of all workouts, summing volumes for the same date.

    :param table: TinyDB table
    :type table: tinydb.table.Table
    :return: List of tuples containing the date and total volume of each workout
    :rtype: list[tuple[str, int]]
    """

    date_and_volume: dict[str, float] = {}

    for item in table:
        workout = item if isinstance(item, dict) else {}
        date = workout.get("date")
        if not isinstance(date, str):
            continue
        mass = positive_number(workout.get("bodyweight_kg"))
        if mass is None and bodyweights is not None:
            mass = positive_number(bodyweights.get(date))
        exercises = workout.get("exercises", {})
        if not isinstance(exercises, dict):
            continue

        total_volume = 0.0
        known_sets = 0
        for sets in exercises.values():
            if not isinstance(sets, list):
                continue
            for exercise_set in sets:
                if not isinstance(exercise_set, dict):
                    continue
                parsed = parse_load(str(exercise_set.get("weight", "")), mass)
                reps = positive_number(exercise_set.get("reps"), allow_zero=True)
                if parsed.total_kg is not None and reps is not None:
                    total_volume += reps * parsed.total_kg * exercise_set.get("load_multiplier", 1)
                    known_sets += 1
        if known_sets:
            date_and_volume[date] = date_and_volume.get(date, 0) + total_volume

    # Convert the dictionary to a list of tuples
    return sorted(date_and_volume.items())


def main() -> None:
    """
    Get the total volume of each workout in the table.
    """

    datatype = "real"
    _, table, _ = set_db_and_table(datatype)
    date_and_volume = get_total_volume(table)
    logger.debug(pformat(date_and_volume))


if __name__ == "__main__":
    main()
