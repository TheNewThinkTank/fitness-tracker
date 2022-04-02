"""
Date: 2021-12-11
Author: Gustav Collin Rasmussen
Purpose: Store and analyze weight-training data
https://tinydb.readthedocs.io/en/latest/getting-started.html
"""

import json
from tinydb import Query, TinyDB  # type: ignore


def get_dates_and_muscle_groups(log):
    """Returns all workout dates with their corresponding muscle groups."""
    return {item["date"]: item["split"] for item in log}


def show_exercises(log, date):
    """Show all exercises for given workout date"""

    all_exercises_during_workout = []

    for item in log:
        if item["date"] == date:
            for k, _ in item["exercises"].items():
                all_exercises_during_workout.append(k)
    return all_exercises_during_workout


def get_all(log):
    """get all documents"""
    return log.all()


def describe_workout(log, date):
    """Simple summary statistics for each exercise"""

    d = {}
    for item in log:
        if item["date"] == date:
            d["Date of workout"] = date

            for k, v in item["exercises"].items():
                d[k] = f"{len(v)} sets"
    return d


def show_exercise(log, exercise, date):
    """Show detailed data for selected exercise"""

    for item in log:
        if item["date"] == date:
            for k, v in item["exercises"].items():
                if k == exercise:
                    return v


def analyze_workout(log, exercise):
    """Deeper analysis of workout"""
    Log = Query()
    data = log.search(Log["exercises"][exercise].exists())
    return [d["exercises"][exercise] for d in data]


def cleanup(db, log, action) -> None:
    """Update, remove or truncate database"""

    # TODO: implement update and remove actions
    # if action == "update":
    #     log.update({"count": 10}, Fruit.type == "apple")

    # if action == "remove":
    #     log.remove(exercises.squat < 5)

    if action == "truncate":
        log.truncate()
        assert log.all() == []


def main():
    datamodels = ["real", "simulated"]
    datatype = datamodels[0]

    data = json.load(open(file="./config.json", encoding="utf-8"))
    db = (
        TinyDB(data["real_workout_database"])
        if datatype == "real"
        else TinyDB(data["simulated_workout_database"])
    )
    table = (
        db.table(data["real_weight_table"])
        if datatype == "real"
        else db.table(data["simulated_weight_table"])
    )

    # dates_and_muscle_groups = get_dates_and_muscle_groups(table)
    # print(dates_and_muscle_groups)
    # print(show_exercises(table, "2021-12-16"))
    # print(describe_workout(table, "2021-12-13"))
    # show_exercise(table, "squat", "2021-12-11")
    print(analyze_workout(table, "squat"))
    # cleanup(db, table, action="truncate")


if __name__ == "__main__":
    main()
