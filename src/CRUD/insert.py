"""
Date: 2021-12-13
Purpose: Store weight-training data
https://tinydb.readthedocs.io/en/latest/getting-started.html
"""

__author__ = "Gustav Collin Rasmussen"
__version__ = "0.1.0"

import glob
import json
import os
import pathlib
import sys
import yaml  # type: ignore

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from helpers import lookup  # type: ignore
from helpers.set_db_and_table import set_db_and_table  # type: ignore


def insert_log(table, log_path: pathlib.Path | list, file_format: str) -> None:
    """Store, file_format training log: log_path in database table.

    :param table: A TinyDB table
    :type table: TinyDB table
    :param log_path: A path to the workout log file
        that will be inserted into the table
    :type log_path: str
    """

    assert log_path

    if isinstance(log_path, str):
        with open(log_path) as rf:
            if file_format == 'json':
                content = json.load(rf)
            elif file_format == 'yml':
                content = yaml.safe_load(rf)
    elif isinstance(log_path, list):
        with open(*log_path) as rf:
            if file_format == 'json':
                content = json.load(rf)
            elif file_format == 'yml':
                content = yaml.safe_load(rf)

    table.insert(content)


def insert_all_logs(table, folderpath: str) -> None:
    """Store all training logs in database.

    :param table: A TinyDB table
    :type table: TinyDB table
    :param folderpath: A path to the workout log folder,
        from where each file will be inserted into the table
    :type folderpath: str
    """

    p = pathlib.Path(folderpath)
    all_files = os.listdir(p)
    for f in all_files:
        insert_log(table, p / f, file_format)


def insert_specific_log(date: str, table, file_format: str, workout_number: int = 1) -> None:
    """Store a specific training log in database.

    :param date: string of date in format YYYY-MM-DD
    :type date: str
    :param table: A TinyDB table
    :type table: TinyDB table
    :param file_format: file extention, e.g. json or yml
    :type file_format: str
    :param workout_number: unique identifier of the workout on a given day,
        in case of multiple workouts. Defaults to 1
    :type workout_number: int, optional
    """

    YEAR, MONTH = lookup.get_year_and_month(date)
    athlete = "gustav_rasmussen"

    with open("local_assets/private_config.json", "r") as private_config:
        DATA = json.load(private_config)
        USER = DATA["user"]
        EMAIL = DATA["email"]

    athlete = "gustav_rasmussen"
    user = USER
    email = EMAIL

    with open("config.yml", "r") as rf:
        DATA = yaml.load(rf, Loader=yaml.FullLoader)

    base_path = (
        DATA["google_drive_data_path"]
        .replace("<ATHLETE>", athlete)
        .replace("<USER>", user)
        .replace("<EMAIL>", email)
    )

    # TODO: add f"/{athlete}/log_archive/YAML/" path to Google Drive
    base_path += f"/{athlete}/log_archive/JSON/{YEAR}/{MONTH}/*training_log_{date}"

    if workout_number > 1:
        base_path += f"_{workout_number}"

    full_path = base_path + '.' + file_format  # "json" "yml"
    log_path = glob.glob(full_path)

    # print(f"{log_path = }")
    insert_log(table, log_path, file_format)


def main() -> None:
    """Insert all simulated- or 1 or more real training logs"""

    import argparse
    import logging

    parser = argparse.ArgumentParser()

    parser.add_argument("--file_format", type=str, default='json')
    parser.add_argument("--datatype", type=str, required=True)
    parser.add_argument("--dates", type=str)
    parser.add_argument("--workout_number", type=int)

    args = parser.parse_args()

    file_format = args.file_format  # json or yml
    datatype = args.datatype  # real/simulated
    dates = args.dates  # 2022-02-03,2022-02-05
    workout_number = args.workout_number

    pathlib.Path("logs/").mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        datefmt="%m-%d %H:%M",
        filename="logs/insert.log",
        filemode="w",
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s")
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)
    logging.info("Running %s ...", "/".join(__file__.split("/")[-4:]))

    db, table, _ = set_db_and_table(datatype)

    logging.info("datatype: %s", datatype)
    logging.debug("db: %s", db)
    logging.debug("table: %s", table)

    if datatype == "real":
        logging.info("workout date(s): %s", dates)
        for date in dates.split(","):
            if args.workout_number is None:
                insert_specific_log(date, table, file_format)
            else:
                insert_specific_log(date, table, file_format, workout_number)
                logging.info("workout number: %s", workout_number)

    elif datatype == "simulated":
        insert_all_logs(table, "data/simulated/")

    else:
        logging.error("Unsupported value for datatype: %s", datatype)


if __name__ == "__main__":
    main()
