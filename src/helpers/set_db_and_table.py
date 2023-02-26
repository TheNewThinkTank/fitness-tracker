"""
Date: 2021-12-27
Purpose: Set db and table depending on datatype (real/simulated)
"""

__all__ = ["set_db_and_table"]
__author__ = "Gustav Collin Rasmussen"
__version__ = "0.1.0"

import json
import yaml  # type: ignore

from tinydb import TinyDB  # type: ignore


def set_db_and_table(
    datatype,
    athlete="somebody",
    user="somebody",
    email="somebody@gmail.com",
):
    """."""

    with open("config.yml", "r") as rf:
        DATA = yaml.load(rf, Loader=yaml.FullLoader)

    DATA = {
        d: DATA[d].replace("<GOOGLE_DRIVE_DATA_PATH>", DATA["google_drive_data_path"])
        for d in DATA
    }

    # db = TinyDB('db.json', sort_keys=True, indent=4, separators=(',', ': '))
    db = (
        TinyDB(
            DATA["real_workout_database"]
            .replace("<ATHLETE>", athlete)
            .replace("<USER>", user)
            .replace("<EMAIL>", email)
        )
        if datatype == "real"
        else TinyDB(
            DATA["simulated_workout_database"],
            sort_keys=True,
            indent=4,
            separators=(",", ": "),
        )
    )
    table = (
        db.table(DATA["real_weight_table"])
        if datatype == "real"
        else db.table(DATA["simulated_weight_table"])
    )
    training_catalogue = DATA["training_catalogue"]

    return db, table, training_catalogue


if __name__ == "__main__":
    with open("local_assets/private_config.json", "r") as private_config:
        DATA = json.load(private_config)
        USER = DATA["user"]
        EMAIL = DATA["email"]

    print(
        set_db_and_table(
            datatype="real",
            athlete="gustav_rasmussen",
            user=USER,
            email=EMAIL,
        )
    )
