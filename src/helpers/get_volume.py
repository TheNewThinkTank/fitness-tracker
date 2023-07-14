"""
_summary_
"""

from pprint import pprint as pp
# from src.helpers.get_bodyweight import get_bw  # type: ignore
# from src.helpers.set_db_and_table import set_db_and_table  # type: ignore
from helpers.get_bodyweight import get_bw  # type: ignore
from helpers.set_db_and_table import set_db_and_table  # type: ignore
# from get_bodyweight import get_bw  # type: ignore
# from set_db_and_table import set_db_and_table  # type: ignore


def get_total_volume(table) -> list[tuple[str, int]]:
    """_summary_

    :param table: _description_
    :type table: _type_
    :return: _description_
    :rtype: list[tuple[str, int]]
    """

    bodyweight = str(get_bw())  # "80"
    date_and_volume = []

    for item in table:
        total_volume = 0

        for exercise in item["exercises"].keys():

            number_of_sets = len(item["exercises"][exercise])
            volume_partial = []

            for s in item["exercises"][exercise]:

                if s["weight"][:-3] != "0":

                    weight = eval(s["weight"][:-3].replace("BODYWEIGHT", bodyweight))

                    volume_partial.append(s["reps"] * weight)

                else:
                    volume_partial.append(s["reps"] * 1)

            total_volume += number_of_sets * max(volume_partial)

        date_and_volume.append((item["date"], total_volume))
    return date_and_volume


def main():
    """_summary_
    """

    datatype = "real"
    _, table, _ = set_db_and_table(datatype)

    date_and_volume = get_total_volume(table)

    pp(date_and_volume)


if __name__ == "__main__":
    main()
