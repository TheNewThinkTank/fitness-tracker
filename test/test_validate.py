
from pprint import pprint as pp
import pytest
from src.utils.validate import Workout
from src.utils.config_loader import ConfigLoader  # type: ignore
from src.utils.file_conversions.load_yaml import load_yaml_file  # type: ignore


def setup():
    """Read data from a JSON file."""

    config = ConfigLoader.load_config()
    file = config["real_workout_database"].replace("<YEAR>", "2024")
    data = load_yaml_file(file)["weight_training_log"]
    return data


@pytest.mark.skip(reason="Skip until src/utils/validate is updated.")
def test_workout():
    data = setup()
    workouts: list[Workout] = [Workout(**item) for item in data.values()]
    pp(workouts)
