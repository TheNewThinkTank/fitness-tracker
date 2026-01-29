# TODO: fix import of 'get_data' from 'model'
# import pytest
# from src.model.plot_model import get_split  # type: ignore


# def test_get_split_1rm():
#     expected = [
#         (["chest", "push"], "bb_bench_press"),
#         (["back", "pull"], "seated_row"),
#         (["legs"], "squat"),
#         (["legs"], "deadlift"),
#     ]
#     assert get_split("1rm") == expected


# def test_get_split_gvt():
#     expected = [
#         (["chest", "push", "chest_and_back"], "bb_bench_press"),
#         (["legs", "legs_and_abs"], "squat"),
#     ]
#     assert get_split("gvt") == expected


# def test_get_split_invalid_program():
#     with pytest.raises(KeyError):
#         get_split("unknown")
