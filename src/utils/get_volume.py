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
        ) -> int:
    """Get the weight of the exercise.

    :param s: Dictionary containing the exercise details
    :type s: dict
    :param bodyweight: Bodyweight of the person in kg
    :type bodyweight: str
    :param Sidea_9012_Olympic_Hex_Bar: Weight of the barbell
    :type Sidea_9012_Olympic_Hex_Bar: str
    :return: Weight of the exercise
    :rtype: float
    """

    weight_expr = (
        s["weight"][:-3]
        .replace("BODYWEIGHT", bodyweight)
        .replace("Sidea_9012_Olympic_Hex_Bar", Sidea_9012_Olympic_Hex_Bar)
    )

    # Replace POWERBAND_COLOR with actual resistance value
    def replace_powerband(match):
        color = match.group(1)
        return str(bands_mapping.get(color, 0))  # Default to 0 if unknown

    weight_expr = re.sub(r"POWERBAND_(GREEN|PURPLE|BLACK|RED)", replace_powerband, weight_expr)

    # Safe evaluation using eval() with restricted scope
    try:
        # Only allow basic math operations; no external functions allowed
        allowed_names = {
            "__builtins__": {},
        }
        result = eval(weight_expr, allowed_names, {})
        return result
    except Exception as e:
        logger.error(f"Error evaluating weight expression: {weight_expr} | {e}")
        return 0


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
