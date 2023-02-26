import json
from pprint import pprint as pp

from context import src
from src.helpers.validate import Workout


def setup():
    """Read data from a JSON file."""

    DATA = json.load(open(file="./config.json", encoding="utf-8"))
    file = DATA["real_workout_database"].replace("<ATHLETE>", "gustav_rasmussen")
    with open(file) as rf:
        data = json.load(rf)["weight_training_log"]
    return data


def test_workout():
    data = setup()
    workouts: list[Workout] = [Workout(**item) for item in data.values()]
    pp(workouts)
