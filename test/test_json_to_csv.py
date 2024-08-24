
import pytest

import pandas as pd  # type: ignore

from test.conftest import src
from src.helpers.json_to_csv import get_exercise_data  # , df_to_csv


# def setup():
#     dircontent = []
#     json_files = "data/gustav_rasmussen/log_archive/JSON/"
#     for path in Path(json_files).rglob("*.json"):
#         if not any(x in path.stem for x in ("template", "yoga")):
#             dircontent.append(path)
#     return dircontent


@pytest.mark.skip(reason="Skip until getting log from Google Drive is implemented.")
def test_get_exercise_data():

    # dircontent = setup()
    # df = get_exercise_data(str(dircontent[0]))

    logfile = "data/gustav_rasmussen/log_archive/JSON/2022/April/push_training_log_2022-04-20.json"
    df = get_exercise_data(logfile)

    data = [
        [1, 6, "'80 kg'", "barbell_bench_press", "2022-04-20", "push"],
        [2, 8, "'70 kg'", "barbell_bench_press", "2022-04-20", "push"],
        [3, 9, "'60 kg'", "barbell_bench_press", "2022-04-20", "push"],
        [1, 5, "'60 kg'", "dumbbell_incline_press", "2022-04-20", "push"],
        [2, 8, "'48 kg'", "dumbbell_incline_press", "2022-04-20", "push"],
        [3, 6, "'48 kg'", "dumbbell_incline_press", "2022-04-20", "push"],
        [1, 5, "'40 kg'", "standing_barbell_military_press", "2022-04-20", "push"],
        [2, 8, "'30 kg'", "standing_barbell_military_press", "2022-04-20", "push"],
        [3, 20, "'15 kg'", "standing_barbell_military_press", "2022-04-20", "push"],
        [1, 12, "'32 kg'", "dumbbell_flys", "2022-04-20", "push"],
        [2, 12, "'32 kg'", "dumbbell_flys", "2022-04-20", "push"],
        [3, 12, "'32 kg'", "dumbbell_flys", "2022-04-20", "push"],
        [1, 8, "'12 kg'", "dumbbell_incline_front_lateral_raise", "2022-04-20", "push"],
        [
            2,
            10,
            "'12 kg'",
            "dumbbell_incline_front_lateral_raise",
            "2022-04-20",
            "push",
        ],
        [3, 8, "'12 kg'", "dumbbell_incline_front_lateral_raise", "2022-04-20", "push"],
        [1, 12, "'24 kg'", "french_press", "2022-04-20", "push"],
        [2, 12, "'24 kg'", "french_press", "2022-04-20", "push"],
    ]

    index = [0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1]

    df_test = pd.DataFrame(
        data=data,
        columns=["set_number", "reps", "weight", "exercise", "date", "split"],
        index=index,
    )

    pd.testing.assert_frame_equal(df, df_test)


"""
for json_file in dircontent:
    df = get_exercise_data(str(json_file))
    df_to_csv(str(json_file), df)
"""
