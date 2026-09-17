"""
Set db and table depending on datatype (real/simulated).
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any

from loguru import logger  # type: ignore
from tinydb import TinyDB  # type: ignore

from src.utils.config import settings  # type: ignore
from src.utils.custom_storage import YAMLStorage  # type: ignore


class TinyDBSingleton:
    """Singleton wrapper around TinyDB instances."""

    _instances: dict[str, "TinyDBSingleton"] = {}
    _lock = Lock()

    def __new__(
        cls, db_path: str, storage: Any = YAMLStorage, **storage_options: Any
    ) -> "TinyDBSingleton":
        path = str(Path(db_path).expanduser().resolve())
        with cls._lock:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            if path not in cls._instances:
                instance = super().__new__(cls)
                instance.db = TinyDB(path, storage=storage, **storage_options)
                cls._instances[path] = instance
            return cls._instances[path]

    def __init__(
        self, db_path: str, storage: Any = YAMLStorage, **storage_options: Any
    ) -> None:
        if not hasattr(self, "db"):
            self.db = TinyDB(db_path, storage=storage, **storage_options)

    def get_db(self) -> TinyDB:
        return self.db

    def close(self) -> None:
        self.close_all()

    @classmethod
    def close_all(cls) -> None:
        """Close and forget every cached TinyDB instance."""
        with cls._lock:
            for instance in cls._instances.values():
                instance.db.close()
            cls._instances = {}


def _database_template(datatype: str, athlete: str | None = None) -> str:
    if datatype not in {"real", "simulated"}:
        raise ValueError("datatype must be either 'real' or 'simulated'")

    resolved_athlete = athlete or str(settings.get("ATHLETE", "default"))
    setting_name = (
        "REAL_WORKOUT_DATABASE"
        if datatype == "real"
        else "SIMULATED_WORKOUT_DATABASE"
    )
    return str(settings[setting_name]).replace("<ATHLETE>", resolved_athlete)


def get_database_path(
    datatype: str,
    athlete: str | None = None,
    year: int | None = None,
) -> Path:
    """Resolve a database path without opening or creating it."""
    resolved_year = year if year is not None else datetime.now().year
    return Path(
        _database_template(datatype, athlete).replace("<YEAR>", str(resolved_year))
    ).expanduser()


def get_available_years(
    datatype: str = "real",
    athlete: str | None = None,
) -> list[int]:
    """Return sorted years that have an existing workout database."""
    template = Path(_database_template(datatype, athlete)).expanduser()
    if "<YEAR>" not in template.name or not template.parent.is_dir():
        return []

    prefix, suffix = template.name.split("<YEAR>", maxsplit=1)
    years: list[int] = []
    for candidate in template.parent.glob(f"{prefix}*{suffix}"):
        year_text = candidate.name[len(prefix):]
        if suffix:
            year_text = year_text[:-len(suffix)]
        if candidate.is_file() and len(year_text) == 4 and year_text.isdigit():
            years.append(int(year_text))
    return sorted(set(years))


def set_db_and_table(
    datatype: str,
    athlete: str | None = None,
    year: int | None = None,
    env: str = "prd",
    create: bool = True,
) -> tuple[TinyDB, Any, str]:
    """Set up database and table based on datatype (real/simulated).
    
    :param datatype: Type of data to be used, either "real" or "simulated"
    :type datatype: str
    :param athlete: Athlete name, defaults to None
    :type athlete: str, optional
    :param year: Year of the data, defaults to None
    :type year: int, optional
    :param env: Environment, defaults to "prd"
    :type env: str, optional
    :return: Database, table and training catalogue
    :rtype: tuple
    """

    if year is None:
        year = datetime.now().year

    training_catalogue = settings["TRAINING_CATALOGUE"]

    database_path = (
        Path("data") / f"{year}_workouts.yml"
        if env != "prd"
        else get_database_path(datatype, athlete, year)
    )
    if not create and not database_path.is_file():
        raise FileNotFoundError(database_path)

    table_name = str(settings[f"{datatype.upper()}_WEIGHT_TABLE"])
    db_singleton = TinyDBSingleton(
        str(database_path), workout_table=table_name, workout_year=year
    )
    db = db_singleton.get_db()
    table = db.table(table_name)

    return db, table, training_catalogue

def main() -> None:
    """Explicitly migrate workout identities in configured databases."""
    import argparse

    parser = argparse.ArgumentParser(description="Persist permanent workout IDs.")
    parser.add_argument("--migrate-ids", action="store_true", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--datatype", choices=["real", "simulated"], default="real")
    parser.add_argument("--year", type=int)
    args = parser.parse_args()
    years = [args.year] if args.year is not None else get_available_years(args.datatype)
    if not years and args.datatype == "simulated":
        years = [datetime.now().year]
    try:
        for year in years:
            database, _, _ = set_db_and_table(args.datatype, year=year, create=False)
            storage = database.storage
            if not isinstance(storage, YAMLStorage):
                raise TypeError("Workout ID migration requires YAML storage")
            count = storage.migrate_workout_ids(dry_run=args.dry_run)
            logger.info(
                "{}: {} workout IDs {}",
                get_database_path(args.datatype, year=year),
                count,
                "to backfill" if args.dry_run else "backfilled",
            )
    finally:
        TinyDBSingleton.close_all()


if __name__ == "__main__":
    main()
