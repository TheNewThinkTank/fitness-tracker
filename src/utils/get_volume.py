"""
Get the total workout volume of each date in the table.
In the case of multiple workouts on the same day,
the volume is the sum of the volumes of the workouts.
"""

from pprint import pformat  # type: ignore
import re
from loguru import logger  # type: ignore
from typing import Any
from src.utils.get_bodyweight import get_bw  # type: ignore
from src.utils.set_db_and_table import set_db_and_table  # type: ignore
from src.utils.powerbands import bands_mapping  # type: ignore


def get_weight(
        s: dict,
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

    raw = s["weight"].strip()

    # Strip trailing " kg" if present
    if raw.endswith(" kg"):
        raw = raw[:-3].strip()

    # Substitute named constants before parsing
    raw = raw.replace("Sidea_9012_Olympic_Hex_Bar", Sidea_9012_Olympic_Hex_Bar)

    # Substitute powerband colors with their resistance values
    def _replace_powerband(match: re.Match) -> str:
        color = match.group(1)
        return str(bands_mapping.get(color, 0))

    raw = re.sub(r"POWERBAND_(GREEN|PURPLE|BLACK|RED)", _replace_powerband, raw)

    # Handle BODYWEIGHT forms: "BODYWEIGHT", "BODYWEIGHT + N", "BODYWEIGHT - N"
    bw_match = re.fullmatch(
        r"BODYWEIGHT(?:\s*([+-])\s*(\d+(?:\.\d+)?))?", raw, re.IGNORECASE
    )
    if bw_match:
        bw = float(bodyweight)
        if bw_match.group(1) is None:
            return bw
        delta = float(bw_match.group(2))
        return bw + delta if bw_match.group(1) == "+" else bw - delta

    # Handle simple arithmetic "A + B" or "A - B" (two numeric terms)
    arith_match = re.fullmatch(
        r"(\d+(?:\.\d+)?)\s*([+-])\s*(\d+(?:\.\d+)?)", raw
    )
    if arith_match:
        a, op, b = float(arith_match.group(1)), arith_match.group(2), float(arith_match.group(3))
        return a + b if op == "+" else a - b

    # Plain numeric
    try:
        return float(raw)
    except ValueError:
        logger.error(f"Cannot parse weight expression: {s['weight']!r}")
        return 0.0


def get_total_volume(table) -> list[tuple[str, int]]:
    """Get the total volume of all workouts, summing volumes for the same date.

    :param table: TinyDB table
    :type table: tinydb.table.Table
    :return: List of tuples containing the date and total volume of each workout
    :rtype: list[tuple[str, int]]
    """

    bodyweight = str(get_bw())
    Sidea_9012_Olympic_Hex_Bar = "31"
    date_and_volume: dict[Any, Any] = {}

    for item in table:
        total_volume = 0
        for exercise in item["exercises"].keys():
            number_of_sets = len(item["exercises"][exercise])
            volume_partial = []

            for s in item["exercises"][exercise]:
                weight = 1
                if s["weight"][:-3] != "0":
                    weight = get_weight(s, bodyweight, Sidea_9012_Olympic_Hex_Bar)
                volume_partial.append(s["reps"] * weight)

            total_volume += number_of_sets * max(volume_partial)

        # Sum volumes for the same date
        date = item["date"]
        if date in date_and_volume:
            date_and_volume[date] += total_volume
        else:
            date_and_volume[date] = total_volume

    # Convert the dictionary to a list of tuples
    return list(date_and_volume.items())


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
