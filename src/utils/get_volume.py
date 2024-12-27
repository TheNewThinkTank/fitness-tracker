"""
Get the total volume of each workout in the table.
"""

from pprint import pprint as pp
from utils.get_bodyweight import get_bw  # type: ignore
from utils.set_db_and_table import set_db_and_table  # type: ignore


def get_weight(s: dict, bodyweight: str, Sidea_9012_Olympic_Hex_Bar: str) -> int:
    """Get the weight of the exercise.

    :param s: Dictionary containing the exercise details
    :type s: dict
    :param bodyweight: Bodyweight of the person
    :type bodyweight: str
    :param Sidea_9012_Olympic_Hex_Bar: Weight of the barbell
    :type Sidea_9012_Olympic_Hex_Bar: str
    :return: Weight of the exercise
    :rtype: float
    """
    weight = eval(
        s["weight"][:-3]
        .replace("BODYWEIGHT", bodyweight)
        .replace("Sidea_9012_Olympic_Hex_Bar", Sidea_9012_Olympic_Hex_Bar)
    )

    return weight


def get_total_volume(table) -> list[tuple[str, int]]:
    """Get the total volume of each workout in the table.

    :param table: TinyDB table
    :type table: tinydb.table.Table
    :return: List of tuples containing the date and total volume of each workout
    :rtype: list[tuple[str, int]]
    """

    bodyweight = str(get_bw())  # "80"
    Sidea_9012_Olympic_Hex_Bar = "31"
    date_and_volume = []
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
        date_and_volume.append((item["date"], total_volume))
    return date_and_volume


def main() -> None:
    """
    Get the total volume of each workout in the table.
    """

    datatype = "real"
    _, table, _ = set_db_and_table(datatype)
    date_and_volume = get_total_volume(table)
    pp(date_and_volume)


if __name__ == "__main__":
    main()
