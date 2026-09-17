"""
Store weight-training data.

Docs: https://tinydb.readthedocs.io/en/latest/getting-started.html
"""

import json
import os
from collections.abc import Sequence
from pathlib import Path
from typing import NewType
from pydantic import ValidationError
from src.common.workout_types import WorkoutData, parse_workout_date
from src.utils.config import settings  # type: ignore
import yaml  # type: ignore
from tinydb import table  # type: ignore
from loguru import logger  # type: ignore
from src.utils.set_db_and_table import set_db_and_table  # type: ignore

WorkoutDate = NewType("WorkoutDate", str)
SUPPORTED_LOG_FORMATS = {"json", "yml"}


def _validate_file_format(file_format: str) -> str:
    normalized_format = file_format.lower()
    if normalized_format not in SUPPORTED_LOG_FORMATS:
        raise ValueError(
            f"Invalid file format: {file_format}. Expected 'json' or 'yml'."
        )
    return normalized_format


def _load_workout_record(
    log_path: Path, file_format: str, expected_date: str | None = None
) -> dict:
    with log_path.open(encoding="utf-8") as handle:
        content = json.load(handle) if file_format == "json" else yaml.safe_load(handle)
    try:
        record = WorkoutData.model_validate(content).model_dump(
            mode="json", exclude_unset=True
        )
    except ValidationError as exc:
        raise ValueError(f"Invalid workout record in {log_path}: {exc}") from exc
    if expected_date is not None and record["date"] != expected_date:
        raise ValueError(f"Workout date in {log_path} does not match {expected_date}")
    return record


def insert_log(
    table: table.Table,
    log_path: str | Path | Sequence[str | Path],
    file_format: str,
    *,
    expected_date: str | None = None,
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

    normalized_format = _validate_file_format(file_format)
    logger.debug(f"{log_path = }")

    if isinstance(log_path, (str, Path)):
        records = [_load_workout_record(Path(log_path), normalized_format, expected_date)]
    elif isinstance(log_path, Sequence):
        if not log_path:
            raise ValueError("No files found for the given date and workout number.")
        records = [
            _load_workout_record(Path(file_path), normalized_format, expected_date)
            for file_path in log_path
        ]
    else:
        raise TypeError(f"Unsupported type for log_path: {type(log_path)}")
    for record in records:
        table.insert(record)


def insert_all_logs(
        table: table.Table,
        folderpath: str,
        file_format: str
    ) -> None:
    """Store all training logs in database.

    :param table: A TinyDB table
    :type table: TinyDB table
    :param folderpath: A path to the workout log folder,
        from where each file will be inserted into the table
    :type folderpath: str
    """

    normalized_format = _validate_file_format(file_format)
    logger.debug(f"{folderpath = }")

    p = Path(folderpath)
    all_files = sorted(path for path in os.listdir(p) if path.endswith(f".{normalized_format}"))
    for f in all_files:
        insert_log(table, p / f, normalized_format)


def insert_specific_log(
        date: WorkoutDate,
        table: table.Table,
        file_format: str="yml",
        workout_number: int=1
    ) -> None:
    """Store a specific training log in database.

    :param date: string of date in format YYYY-MM-DD
    :type date: str
    :param TableName(table): A TinyDB TableName(table)
    :type TableName(table): TinyDB TableName(table)
    :param file_format: file extention, e.g. json or yml
    :type file_format: str
    :param workout_number: unique identifier of the workout on a given day,
        in case of multiple workouts. Defaults to 1
    :type workout_number: int, optional
    """

    normalized_format = _validate_file_format(file_format)
    parsed_date = parse_workout_date(date)
    if workout_number < 1:
        raise ValueError("workout_number must be at least 1")

    data_root = Path(settings["DATA_DIR"]).expanduser().resolve()
    base_path = (
        data_root
        / "log_archive"
        / normalized_format.upper()
        / str(parsed_date.year)
        / parsed_date.strftime("%B")
    ).resolve()
    if not base_path.is_relative_to(data_root):
        raise ValueError("Workout archive path escapes DATA_DIR")

    file_pattern = f"*training_log_{parsed_date.isoformat()}"
    if workout_number > 1:
        file_pattern += f"_{workout_number}"
    file_pattern += f".{normalized_format}"

    full_path = base_path / file_pattern
    logger.debug(f"Searching for files matching: {full_path}")
    log_path = [
        path
        for path in base_path.glob(file_pattern)
        if path.is_file() and path.resolve().is_relative_to(base_path)
    ]

    logger.debug(f"{full_path = }")
    logger.debug(f"{log_path = }")

    if not log_path:
        raise FileNotFoundError(f"No files found for date {date} and workout number {workout_number}.")

    insert_log(table, log_path, normalized_format, expected_date=parsed_date.isoformat())


def main() -> None:
    """Insert all simulated- or 1 or more real training logs.
    """

    import argparse
    from src.utils.logger_config import setup_logger, log_running_file  # type: ignore

    setup_logger(log_file="insert.log")
    log_running_file(__file__)

    parser = argparse.ArgumentParser(
        description="Add workout logs to TinyDB.",
    )

    parser.add_argument(
        "-f",
        "--file_format",
        type=str,
        default="yml",
        help="Format of the workout log file.",
    )

    parser.add_argument(
        "-t",
        "--datatype",
        type=str,
        default="real",
        help="Either real or simulated workout data.",
    )

    parser.add_argument(
        "-d",
        "--dates",
        type=str,
        help="Date the workout was performed on.",
    )

    parser.add_argument(
        "-w",
        "--workout_number",
        type=int,
        help="Number of workouts, if there are multiple workouts on a given date.",
    )

    args = parser.parse_args()

    file_format = args.file_format
    datatype = args.datatype
    dates = args.dates
    workout_number = args.workout_number

    logger.info("datatype: {}", datatype)

    if datatype == "real":
        if not dates:
            parser.error("--dates is required for real workout imports")
        logger.info("workout date(s): {}", dates)
        for date in dates.split(","):
            parsed_date = parse_workout_date(date)
            db, table, _ = set_db_and_table(datatype, year=parsed_date.year)
            if args.workout_number is None:
                insert_specific_log(WorkoutDate(date), table, file_format)
            else:
                insert_specific_log(WorkoutDate(date), table, file_format, workout_number)
                logger.info("workout number: {}", workout_number)

    elif datatype == "simulated":
        db, table, _ = set_db_and_table(datatype)
        insert_all_logs(table, "data/simulated/", file_format)

    else:
        logger.error("Unsupported value for datatype: {}", datatype)


if __name__ == "__main__":
    main()
