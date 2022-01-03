"""
Date: 2021-12-13
Author: Gustav Collin Rasmussen
Purpose: Store weight-training data
https://tinydb.readthedocs.io/en/latest/getting-started.html
"""

import json
import os
import pathlib

from tinydb import TinyDB


def insert_log(table, log_path) -> None:
    """Store training log: log_path in database table"""
    with open(log_path) as rf:
        json_content = json.load(rf)
    table.insert(json_content)


def insert_all_logs(table, folderpath):
    """Store all training logs in database"""

    p = pathlib.Path(folderpath)
    all_files = os.listdir(p)
    for f in all_files:
        insert_log(table, p / f)


def insert_specific_log(date, table):
    """Store a specific training log in database"""
    months = {
        "01": "January",
        "02": "February",
        "03": "March",
        "04": "April",
        "05": "May",
        "06": "June",
        "07": "July",
        "08": "August",
        "09": "September",
        "10": "October",
        "11": "November",
        "12": "December",
    }

    YEAR = date[:4]
    MONTH = months[date[5:7]]
    log_path = f"data/log_archive/JSON/{YEAR}/{MONTH}/training_log_{date}.json"

    insert_log(table, log_path)


def main():
    """Insert training log from specific date"""
    data_models = ["real", "simulated"]
    data_model = data_models[0]

    db = TinyDB("data/db.json") if data_model == "real" else TinyDB("data/sim_db.json")
    logs = ["weight_training_log", "disciplines_log"]
    table = db.table(logs[0])

    if data_model == "real":
        date = "2022-01-03"
        insert_specific_log(date, table)

        """
        dates = [
            "2021-12-11",
            "2021-12-13",
            "2021-12-15",
            "2021-12-16",
            "2021-12-25",
            "2021-12-26",
            "2021-12-28",
            "2021-12-29",
        ]
        for date in dates:
            insert_specific_log(date, table)
        """

    elif data_model == "simulated":
        insert_all_logs(table, "data/simulated/")

    else:
        print("Unsupported data_model")


if __name__ == "__main__":
    main()
