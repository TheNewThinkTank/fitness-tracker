"""
Date: 2021-12-11
Author: Gustav Collin Rasmussen
Purpose: Store and analyze weight-training data
https://tinydb.readthedocs.io/en/latest/getting-started.html
"""

from tinydb import Query, TinyDB


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


def analyze_workout(db, log):
    """Deeper analysis of workout"""
    Log = Query()
    # Exercise = Query()
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
    db = TinyDB("data/db.json")
    log = db.table("log")

    # dates_and_muscle_groups = get_dates_and_muscle_groups(log)
    # print(dates_and_muscle_groups)

    print(show_exercises(log, "2021-12-16"))

    # print(describe_workout(log, "2021-12-13"))
    # show_exercise(log, "squat", "2021-12-11")
    # analyze_workout(db, log)
    # cleanup(db)


if __name__ == "__main__":
    main()