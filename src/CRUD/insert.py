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
from pathlib import Path
import sys
from typing import Union
import yaml  # type: ignore

from tinydb import table  # , TinyDB

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from helpers import lookup  # type: ignore
from helpers.set_db_and_table import set_db_and_table  # type: ignore


def insert_log(table: table.Table,
               log_path: Union[str, Path, list],
               file_format: str) -> None:
    """Store training log from log_path in database table.

    :param table: A TinyDB table
    :type table: TinyDB table
    :param log_path: A path to the workout log file or a list of paths
        that will be inserted into the table
    :type log_path: Union[str, Path, list]
    :param file_format: Format of the log file ('json' or 'yml')
    :type file_format: str
    """

    if isinstance(log_path, list):
        log_paths = log_path
    else:
        log_paths = [log_path]

    content = []

    for path in log_paths:
        with open(path) as rf:
            if file_format == 'json':
                content.extend(json.load(rf))
            elif file_format == 'yml':
                content.extend(yaml.safe_load(rf))

    table.insert_multiple(content)


def insert_all_logs(table, folderpath: str, file_format: str) -> None:
    """Store all training logs in database.

    :param table: A TinyDB table
    :type table: TinyDB table
    :param folderpath: A path to the workout log folder,
        from where each file will be inserted into the table
    :type folderpath: str
    """

    print(f"{folderpath = }")

    p = Path(folderpath)
    all_files = os.listdir(p)
    for f in all_files:
        insert_log(table, p / f, file_format)


def insert_specific_log(date: str,
                        table,
                        file_format: str,
                        workout_number: int = 1) -> None:
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

    with open("config.yml", "r") as rf:
        DATA = yaml.load(rf, Loader=yaml.FullLoader)

    base_path = (
        DATA["google_drive_data_path"]
        .replace("<ATHLETE>", athlete)
        .replace("<USER>", USER)
        .replace("<EMAIL>", EMAIL)
    )

    base_path += f"/{athlete}/log_archive/{file_format.upper()}/{YEAR}/{MONTH}/*training_log_{date}"

    if workout_number > 1:
        base_path += f"_{workout_number}"

    full_path = base_path + '.' + file_format  # json or yml
    log_path = glob.glob(full_path)

    print(f"{full_path = }")
    print(f"{log_path = }")

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

    Path("logs/").mkdir(parents=True, exist_ok=True)
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
        insert_all_logs(table, "data/simulated/", file_format)

    else:
        logging.error("Unsupported value for datatype: %s", datatype)


if __name__ == "__main__":
    main()
