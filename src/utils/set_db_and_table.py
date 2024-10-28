"""
Date: 2021-12-27
Purpose: Set db and table depending on datatype (real/simulated)
"""

from datetime import datetime
from tinydb import TinyDB  # type: ignore
from custom_storage import YAMLStorage  # type: ignore
from config_loader import ConfigLoader  # type: ignore


class TinyDBSingleton:
    _instance = None

    def __new__(cls, db_path, storage=YAMLStorage):
        if cls._instance is None:
            cls._instance = super(TinyDBSingleton, cls).__new__(cls)
            cls._instance.db = TinyDB(db_path, storage=storage)
        return cls._instance

    def get_db(self):
        return self.db

    def close(self):
        if self._instance:
            self.db.close()  # Close the db file, this ensures no further writes.
            TinyDBSingleton._instance = None  # Reset the instance


def set_db_and_table(
    datatype, 
    athlete=None, 
    year=None, 
    env="prd"  # dev
):
    """Set up database and table based on datatype (real/simulated)."""

    env_vars = ConfigLoader.load_env_variables()

    if not athlete:
        athlete = env_vars["athlete"]

    if not year:
        year = datetime.now().year

    config = ConfigLoader.load_config(
        athlete=athlete,
        user=env_vars["user"],
        email=env_vars["email"],
    )

    if env != "prd":
        db = TinyDB(f"data/{year}_workouts.yml", storage=YAMLStorage)
        table = db.table("weight_training_log")
        training_catalogue = "src/utils/muscles_and_exercises.yaml"
        return db, table, training_catalogue

    db_path = (
        config["real_workout_database"]
        .replace("<ATHLETE>", athlete)
        .replace("<YEAR>", str(year))
    ) if datatype == "real" else config["simulated_workout_database"]

    db_singleton = TinyDBSingleton(db_path)
    db = db_singleton.get_db()
    table = db.table(config[f"{datatype}_weight_table"])
    training_catalogue = config["training_catalogue"]

    return db, table, training_catalogue


def main():
    db, table, training_catalogue = set_db_and_table(
        datatype="real",
        year="2021"
    )
    print(db, table, training_catalogue)

    # At the end, make sure to close the database
    db_singleton = TinyDBSingleton("dummy_path")  # Create a dummy instance just to close
    db_singleton.close()


if __name__ == "__main__":
    main()
