"""Get the workout program based on the workout date.
"""

from datetime import datetime as dt
from pathlib import Path
import yaml  # type: ignore


def load_yaml_file(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def parse_date(date_str):
    if isinstance(date_str, str) and any(x in date_str for x in "YMD"):
        return None
    return dt.strptime(date_str, "%Y-%m-%d") if isinstance(date_str, str) else date_str


def get_pgm_from_date(workout_date):
    """Get the workout program based on the workout date.

    :param workout_date: date in the format 'YYYY-MM-DD'
    :type workout_date: str
    :return: name of the workout program
    :rtype: str
    """

    # programs = []
    # with open(".config/config.yml", 'r') as rf:
    #     DATA = yaml.safe_load(rf)
    # workout_programs = DATA["workout_programs"]
    # cwd = Path.cwd()
    # workout_programs = cwd / workout_programs
    # with open(workout_programs, "r") as rf:
    #     available_programs = yaml.load(rf, Loader=yaml.FullLoader)
    # for pgm in available_programs["programs"]:
    #     name = available_programs["programs"][pgm]["name"]
    #     start = available_programs["programs"][pgm]["start"]
    #     end = available_programs["programs"][pgm]["end"]
    #     if isinstance(start, str):
    #         if any(x in start for x in "YMD"):
    #             continue
    #         start = dt.strptime(start, "%Y-%m-%d")
    #     if isinstance(end, str):
    #         if any(x in end for x in "YMD"):
    #             continue
    #         end = dt.strptime(end, "%Y-%m-%d")
    #     programs.append({"name": name, "start": start, "end": end})
    # workout_date = dt.strptime(workout_date, "%Y-%m-%d").date()
    # for pgm in programs:
    #     if pgm["start"] <= workout_date <= pgm["end"]:
    #         return pgm["name"]

    config_data = load_yaml_file(".config/config.yml")
    workout_programs_path = Path.cwd() / config_data["workout_programs"]
    available_programs = load_yaml_file(workout_programs_path)

    programs = []
    for pgm in available_programs["programs"].values():
        start = parse_date(pgm["start"])
        end = parse_date(pgm["end"])
        if start and end:
            programs.append({"name": pgm["name"], "start": start, "end": end})

    workout_date = dt.strptime(workout_date, "%Y-%m-%d").date()
    for pgm in programs:
        if pgm["start"] <= workout_date <= pgm["end"]:
            return pgm["name"]

    return None


def main():
    """Get the workout program based on the workout date.
    """

    workout_date = "2022-01-01"
    print(get_pgm_from_date(workout_date))


if __name__ == "__main__":
    main()
