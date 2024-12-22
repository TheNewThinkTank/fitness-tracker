
from test.conftest import src
from src.utils.get_exercises import get_available_exercises
from src.utils.set_db_and_table import set_db_and_table  # type: ignore


def test_get_available_exercises():

    _, _, training_catalogue = set_db_and_table(datatype="real")
    available_exercises = get_available_exercises(training_catalogue, "back")

    assert available_exercises == [
        "lat_pulldown",
        "bent_over_row",
        "seated_row",
        "chinup",
        "reverse_grip_chinup",
        "pullup",
        "face_pull",
        "bb_shrug",
    ]
