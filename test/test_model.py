"""
    unit test suite for model
"""

import pytest

import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from src.model.model import get_df  # , one_rep_max_estimator

from tinydb import TinyDB


db = TinyDB("../data/sim_db.json")
# db = TinyDB("data/sim_db.json")
table = db.table("weight_training_log")


@pytest.mark.parametrize(
    "test_input_split,test_input_exercise",
    [("legs", "squat")],  # , ('chest', 'pullover')],
)
def test_get_df(test_input_split, test_input_exercise):
    """Verify that blabla."""
    assert len(get_df(table, test_input_split, test_input_exercise)) > 2


# def test_one_rep_max_estimator(df):
#     """Verify that blabla."""
#     pass
