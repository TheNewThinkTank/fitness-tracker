# # TODO: fix import
# from tinydb import TinyDB
# from test.conftest import src
# from src.crud.update import (  # type: ignore
#     # filter_exercises_with_whitespace,
#     clean_exercise_name,
#     # clean_exercise_names
# )


# def setup():
#     MOCK_DB = TinyDB("test/test_db.json")
#     test_table = MOCK_DB.table("test_log")
#     return test_table


# def test_clean_exercise_name():
#     assert clean_exercise_name("bench press") == "bench_press"
#     assert clean_exercise_name("bench  press") == "bench_press"
#     assert clean_exercise_name("bench_press") == "bench_press"
#     assert clean_exercise_name("bench_ press") == "bench_press"
#     assert clean_exercise_name("bench_  press") == "bench_press"
#     assert clean_exercise_name("bench  _  press") == "bench_press"
#     assert clean_exercise_name("shoulder press_") == "shoulder_press"
