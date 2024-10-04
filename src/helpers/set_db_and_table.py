"""
Date: 2021-12-27
Purpose: Set db and table depending on datatype (real/simulated)
"""

from datetime import datetime
import json
import yaml  # type: ignore
from tinydb import TinyDB  # type: ignore
from custom_storage import YAMLStorage  # type: ignore
from config_loader import ConfigLoader  # type: ignore


def set_db_and_table(
    datatype, 
    athlete=None, 
    year=None, 
    env="prd"  # dev
):
    """Set up database and table based on datatype (real/simulated)."""

    if not athlete:
        athlete = ConfigLoader.load_env_variables()["athlete"]

    if not year:
        year = datetime.now().year

    config = ConfigLoader.load_config(
        athlete=athlete,
        user=ConfigLoader.load_env_variables()["user"],
        email=ConfigLoader.load_env_variables()["email"],
    )

    if env != "prd":
        db = TinyDB(f"data/{year}_workouts.yml", storage=YAMLStorage)
        table = db.table("weight_training_log")
        training_catalogue = "src/helpers/muscles_and_exercises.yaml"
        return db, table, training_catalogue

    db_path = (
        config["real_workout_database"]
        .replace("<ATHLETE>", athlete)
        .replace("<YEAR>", str(year))
    ) if datatype == "real" else config["simulated_workout_database"]

    db = TinyDB(db_path, storage=YAMLStorage)
    table = db.table(config[f"{datatype}_weight_table"])
    training_catalogue = config["training_catalogue"]

    return db, table, training_catalogue


def main():
    db, table, training_catalogue = set_db_and_table(
        datatype="real",
        # athlete="gustav_rasmussen",
        year="2021"
    )
    print(db, table, training_catalogue)


if __name__ == "__main__":
    main()
