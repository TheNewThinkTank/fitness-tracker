"""
Set db and table depending on datatype (real/simulated).
"""

from datetime import datetime
import os
from pprint import pprint as pp
from loguru import logger  # type: ignore
from src.utils.config import settings  # type: ignore
from tinydb import TinyDB  # type: ignore
from src.utils.custom_storage import YAMLStorage  # type: ignore


class TinyDBSingleton:
    """Singleton class for TinyDB.
    """
    _instances: dict[str, 'TinyDBSingleton'] = {}

    def __new__(cls, db_path: str, storage=YAMLStorage):
        # Ensure the directory for db_path exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        if db_path not in cls._instances:
            instance = super(TinyDBSingleton, cls).__new__(cls)
            instance.db = TinyDB(db_path, storage=storage)
            cls._instances[db_path] = instance
        return cls._instances[db_path]

    def __init__(self, db_path: str, storage=YAMLStorage):
        if not hasattr(self, 'db'):
            self.db = TinyDB(db_path, storage=storage)

    def get_db(self):
        return self.db

    def close(self):
        for instance in self._instances.values():
            instance.db.close()  # Close the db file, this ensures no further writes.
        TinyDBSingleton._instances = {}  # Reset the instances


def set_db_and_table(
    datatype,
    athlete=None,
    year=None,
    env="prd"  # dev
):
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

    logger.debug(f"{settings = }")

    if not athlete:
        athlete = os.getenv(
            "ATHLETE",
            settings.ATHLETE
            )

    if not year:
        year = datetime.now().year

    if env != "prd" or 'GITHUB_ACTIONS' in os.environ:
        db = TinyDB(f"data/{year}_workouts.yml", storage=YAMLStorage)
        table = db.table("weight_training_log")
        training_catalogue = "src/utils/muscles_and_exercises.yaml"
        return db, table, training_catalogue

    db_path = (
        settings["REAL_WORKOUT_DATABASE"]
        .replace("<YEAR>", str(year))
    ) if datatype == "real" else settings["simulated_workout_database"]

    db_singleton = TinyDBSingleton(db_path)
    db = db_singleton.get_db()
    table = db.table(settings[f"{datatype.upper()}_WEIGHT_TABLE"])
    training_catalogue = settings["TRAINING_CATALOGUE"]

    return db, table, training_catalogue


def main() -> None:
    """Main function.
    """

    # settings = settings.as_dict()
    logger.debug(settings.ATHLETE)

    # db, table, training_catalogue = set_db_and_table(
    #     datatype="real",
    #     year="2021"
    # )

    # logger.debug(db, table, training_catalogue)

    # # At the end, make sure to close the database
    # db_singleton = TinyDBSingleton("dummy_path")  # Create a dummy instance just to close
    # db_singleton.close()


if __name__ == "__main__":
    main()
