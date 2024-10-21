"""."""

import datetime
from pathlib import Path

import yaml  # type: ignore


def get_pgm_from_date(workout_date):
    """_summary_

    :param workout_date: _description_
    :type workout_date: _type_
    :return: _description_
    :rtype: _type_
    """

    programs = []

    with open(".config/config.yml", 'r') as rf:
        DATA = yaml.safe_load(rf)

    workout_programs = DATA["workout_programs"]

    # current_path = Path(__file__).resolve().parent
    cwd = Path.cwd()
    workout_programs = cwd / workout_programs

    with open(workout_programs, "r") as rf:
        available_programs = yaml.load(rf, Loader=yaml.FullLoader)

    for pgm in available_programs["programs"]:
        name = available_programs["programs"][pgm]["name"]
        start = available_programs["programs"][pgm]["start"]
        end = available_programs["programs"][pgm]["end"]

        if isinstance(start, str):
            if any(x in start for x in "YMD"):
                continue
            start = datetime.datetime.strptime(start, "%Y-%m-%d")

        if isinstance(end, str):
            if any(x in end for x in "YMD"):
                continue
            end = datetime.datetime.strptime(end, "%Y-%m-%d")

        programs.append({"name": name, "start": start, "end": end})

    workout_date = datetime.datetime.strptime(workout_date, "%Y-%m-%d").date()

    for pgm in programs:
        if pgm["start"] <= workout_date <= pgm["end"]:
            return pgm["name"]


def main():
    """_summary_
    """

    workout_date = "2022-01-01"
    print(get_pgm_from_date(workout_date))


if __name__ == "__main__":
    main()
