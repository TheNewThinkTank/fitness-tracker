import os
from pprint import pprint as pp
import pytest

from dotenv import load_dotenv
import yaml

from test.conftest import src
from src.utils.validate import Workout

load_dotenv()
email = os.environ["EMAIL"]


def setup():
    """Read data from a JSON file."""

    # DATA = json.load(open(file="./config.json", encoding="utf-8"))
    with open("./.config/config.yml", "r") as rf:
        DATA = yaml.safe_load(rf)

    user = "gustavcollinrasmussen"
    athlete = "gustav_rasmussen"

    google_drive_data_path = (
        DATA["google_drive_data_path"]
        .replace("<USER>", user)
        .replace("<EMAIL>", email)
    )

    file = (
        DATA["real_workout_database"]
        .replace("<GOOGLE_DRIVE_DATA_PATH>", google_drive_data_path)
        .replace("<ATHLETE>", athlete)
        .replace("<YEAR>", "2024")
    )

    with open(file) as rf:
        data = yaml.safe_load(rf)["weight_training_log"]
    return data


@pytest.mark.skip(reason="Skip until src/utils/validate is updated.")
def test_workout():
    data = setup()
    workouts: list[Workout] = [Workout(**item) for item in data.values()]
    pp(workouts)
