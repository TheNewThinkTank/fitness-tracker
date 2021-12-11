"""
Date: 2021-12-11
Author: Gustav Collin Rasmussen
Purpose: Store and analyze weight-training data
https://tinydb.readthedocs.io/en/latest/getting-started.html
"""

import json
from pprint import pprint as pp

from tinydb import Query, TinyDB


def insert_data(db, log):
    """Store training log in database"""
    log_path = "training_log.json"
    with open(log_path) as rf:
        json_content = json.load(rf)
    log.insert(json_content)


def describe_workout(log):
    """Simple summary statistics for each exercise"""
    # get all documents
    # print(log.all())

    for item in log:
        d = {"Date of workout": item["date"]}

    summary = {k: f"{len(v)} sets" for k, v in item["exercises"].items()}
    return {**d, **summary}


def show_exercise(log, exercise):
    """Show data for selected exercise"""

    for item in log:
        for k, v in item["exercises"].items():
            if k == exercise:
                # print(k)
                # pp(v)
                return v  # k


def analyze_workout(db, log):
    """Deeper analysis of workout"""
    Log = Query()
    Exercise = Query()
    # print(log.search(Exercise.date == "2021-12-11"))
    print(log.search(Log.exercises == "squat"))
    # print(log.search(Log.exercises.any(Exercise.name == "squat")))
    # print(db.search(Exercise.exercises.all(Exercise.name == "squat")))
    # print(log.search(Log.exercises.all(Exercise.name == "squat")))


def cleanup(db):
    """Update, remove or truncate database"""
    # db.update({'count': 10}, Fruit.type == 'apple')
    # db.all()

    # db.remove(Fruit.count < 5)
    # db.all()

    # db.truncate()
    # db.all()
    return


def main():
    db = TinyDB("db.json")
    log = db.table("log")

    # insert_data(db, log)
    describe_workout(log)
    show_exercise(log, "squat")
    # analyze_workout(db, log)
    # cleanup(db)


if __name__ == "__main__":
    main()
