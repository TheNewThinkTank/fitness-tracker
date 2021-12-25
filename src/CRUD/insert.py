"""
Date: 2021-12-13
Author: Gustav Collin Rasmussen
Purpose: Store weight-training data
https://tinydb.readthedocs.io/en/latest/getting-started.html
"""

import json

from tinydb import TinyDB


def insert_data(table, log_path):
    """Store training log: log_path in database table"""
    with open(log_path) as rf:
        json_content = json.load(rf)
    table.insert(json_content)


def main(date):
    """Insert training log from specific date"""
    db = TinyDB("data/db.json")
    log = db.table("log")

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
    insert_data(log, log_path)


if __name__ == "__main__":
    date = "2021-12-25"
    main(date)
