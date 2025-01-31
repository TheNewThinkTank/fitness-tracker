"""
Store weight-training data.

Docs: https://tinydb.readthedocs.io/en/latest/getting-started.html
"""

# import glob
import json
import os
from pathlib import Path
from typing import Union
from src.utils.config import settings  # type: ignore
import yaml  # type: ignore
from tinydb import table  # , TinyDB
from icecream import ic  # type: ignore
from datetime_tools.lookup import get_year_and_month  # type: ignore
from src.utils.set_db_and_table import set_db_and_table  # type: ignore


def insert_log(
    table: table.Table,
    log_path: Union[str, Path, list],
    file_format: str
    ) -> None:
    """Store training log from log_path in database table.

    :param table: A TinyDB table
    :type table: TinyDB table
    :param log_path: A path to the workout log file or a list of paths
        that will be inserted into the table
    :type log_path: Union[str, Path, list]
    :param file_format: Format of the log file ('json' or 'yml')
    :type file_format: str
    """

    # Validate file format
    if file_format not in ['json', 'yml']:
        raise ValueError(
            f"Invalid file format: {file_format}. Expected 'json' or 'yml'."
            )

    # assert log_path
    print(f"{log_path = }")

    # Convert Path objects to strings
    if isinstance(log_path, Path):
        log_path = str(log_path)

    if isinstance(log_path, str):
        with open(log_path) as rf:
            if file_format == 'json':
                content = json.load(rf)
            elif file_format == 'yml':
                content = yaml.safe_load(rf)
            table.insert(content)
    elif isinstance(log_path, list):
        if not log_path:
            raise ValueError("No files found for the given date and workout number.")
        for file_path in log_path:
            with open(file_path) as rf:
                if file_format == 'json':
                    content = json.load(rf)
                elif file_format == 'yml':
                    content = yaml.safe_load(rf)
                table.insert(content)
    else:
        raise TypeError(f"Unsupported type for log_path: {type(log_path)}")


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


def insert_specific_log(
    date: str,
    table,
    file_format: str="yml",
    workout_number: int=1
    ) -> None:
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

    YEAR, MONTH = get_year_and_month(date)
    base_path = Path(settings["GOOGLE_DRIVE_DATA_PATH"])

    # base_path += (
    #     f"/{settings['ATHLETE']}/log_archive/{file_format.upper()}/"
    #     f"{YEAR}/{MONTH}/*training_log_{date}"
    # )

    base_path = base_path / settings['ATHLETE'] / "log_archive" / file_format.upper() / str(YEAR) / MONTH

    # Construct the file pattern
    file_pattern = f"*training_log_{date}"

    # TODO: update logic to handle multiple workouts on a given day
    if workout_number > 1:
        # base_path += f"_{workout_number}"
        file_pattern += f"_{workout_number}"
    file_pattern += f".{file_format}"

    # full_path = base_path + '.' + file_format  # json or yml
    full_path = base_path / file_pattern
    print(f"Searching for files matching: {full_path}")
    # /Users/gustavcollinrasmussen/Library/CloudStorage/GoogleDrive-/My Drive/DATA/fitness-tracker-data/gustav_rasmussen/log_archive/YML/2025/January/*training_log_2025-01-29.yml

    # Use glob to find matching files
    # log_path = glob.glob(full_path)
    log_path = list(base_path.glob(file_pattern))

    print(f"{full_path = }")
    print(f"{log_path = }")

    if not log_path:
        raise FileNotFoundError(f"No files found for date {date} and workout number {workout_number}.")

    insert_log(table, log_path, file_format)


def main() -> None:
    """Insert all simulated- or 1 or more real training logs.
    """

    import argparse
    import logging
    from src.utils.logger_config import setup_logger, log_running_file  # type: ignore

    setup_logger(log_file="insert.log")
    log_running_file(__file__)

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

    db, table, _ = set_db_and_table(datatype)
    ic(db)

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
