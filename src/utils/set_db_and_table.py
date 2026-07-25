"""
Set db and table depending on datatype (real/simulated).
"""

from datetime import datetime
import os
from pprint import pformat  # type: ignore
from typing import Any
from loguru import logger  # type: ignore
from src.utils.config import settings  # type: ignore
from tinydb import TinyDB  # type: ignore
from src.utils.custom_storage import YAMLStorage  # type: ignore


class TinyDBSingleton:
    """Singleton wrapper around TinyDB instances."""

    _instances: dict[str, "TinyDBSingleton"] = {}

    def __new__(cls, db_path: str, storage: Any = YAMLStorage) -> "TinyDBSingleton":
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        if db_path not in cls._instances:
            instance = super().__new__(cls)
            instance.db = TinyDB(db_path, storage=storage)
            cls._instances[db_path] = instance
        return cls._instances[db_path]

    def __init__(self, db_path: str, storage: Any = YAMLStorage) -> None:
        if not hasattr(self, "db"):
            self.db = TinyDB(db_path, storage=storage)

    def get_db(self) -> TinyDB:
        return self.db

    def close(self) -> None:
        for instance in self._instances.values():
            instance.db.close()
        TinyDBSingleton._instances = {}


def set_db_and_table(
    datatype: str,
    athlete: str | None = None,
    year: int | None = None,
    env: str = "prd",
) -> tuple[Any, Any, str]:
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

    logger.debug(pformat(settings))

    if not athlete:
        athlete = os.getenv("ATHLETE", settings.ATHLETE)

    if year is None:
        year = datetime.now().year

    training_catalogue = settings["TRAINING_CATALOGUE"]

    if datatype not in {"real", "simulated"}:
        raise ValueError("datatype must be either 'real' or 'simulated'")

    if env != "prd" or "GITHUB_ACTIONS" in os.environ:
        db = TinyDB(f"data/{year}_workouts.yml", storage=YAMLStorage)
        table = db.table("weight_training_log")
        return db, table, training_catalogue

    db_path = (
        settings["REAL_WORKOUT_DATABASE"].replace("<YEAR>", str(year))
        if datatype == "real"
        else settings["simulated_workout_database"]
    )

    db_singleton = TinyDBSingleton(db_path)
    db = db_singleton.get_db()
    table = db.table(settings[f"{datatype.upper()}_WEIGHT_TABLE"])

    return db, table, training_catalogue

def main() -> None:
    """Main function.
    """
    logger.debug(settings.ATHLETE)


if __name__ == "__main__":
    main()
