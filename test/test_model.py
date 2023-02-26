"""
unit test suite for model
"""

import pytest

from context import src
from src.model.model import get_df, one_rep_max_estimator, get_data
from src.helpers.set_db_and_table import set_db_and_table  # type: ignore

datatype = "real"
db, table, _ = set_db_and_table(datatype)


@pytest.mark.parametrize(
    "test_input_split,test_input_exercise",
    [("legs", "squat")],  # , ('chest', 'pullover')],
)
def test_get_df(test_input_split, test_input_exercise):
    """Verify that dataframe has more than 2 entries."""
    df = get_df(table, test_input_split, test_input_exercise)
    assert len(df) > 2


def test_one_rep_max_estimator():
    """Verify that 1RM has progression."""
    df = get_df(table, "legs", "squat")
    df_1rm = one_rep_max_estimator(df)
    # Check that for program_1, first squat 1RM is less or equal to 1RM of last squat
    assert df_1rm.loc["2021-12-11", "1RM"] <= df_1rm.loc["2022-03-14", "1RM"]


def test_get_data():
    """Verify that the correct lists (timestamps and 1RM estimates) are returned,
    for real training data from program_1
    """
    df = get_df(table, "legs", "squat")
    df_1rm = one_rep_max_estimator(df)
    x, y = get_data(df_1rm)

    # real_x_program_1 = [
    # 1639350000.0,
    # 1640473200.0,
    # 1641164400.0,
    # 1642287600.0,
    # 1643410800.0,
    # 1644274800.0,
    # 1644879600.0,
    # 1645916400.0,
    # 1646607600.0,
    # 1647298800.0,
    #     1639177200.0,
    #     1640386800.0,
    #     1640991600.0,
    #     1642201200.0,
    #     1643238000.0,
    #     1644015600.0,
    #     1644620400.0,
    #     1645830000.0,
    #     1646434800.0,
    #     1647212400.0,
    # ]
    real_y_program_1 = [
        102.86,
        91.43,
        102.86,
        108.11,
        108.11,
        108.11,
        108.11,
        108.11,
        114.29,
        114.29,
    ]

    # TODO: assert x[:10] == real_x_program_1
    assert y[:10] == real_y_program_1
