"""
unit test suite for model
"""

from datetime import datetime
import pytest

import pandas as pd

from test.conftest import src
from src.model.model import get_df, one_rep_max_estimator, get_data
from src.helpers.set_db_and_table import set_db_and_table  # type: ignore

pytestmark = pytest.mark.skip(reason="Skip module until PermissionError is fixed")


def setup():
    datatype = "real"
    _, table_2021, _ = set_db_and_table(
        datatype,
        year=datetime.strptime("2021", "%Y").year
        )
    _, table_2022, _ = set_db_and_table(
        datatype,
        year=datetime.strptime("2022", "%Y").year
        )
    return table_2021, table_2022


@pytest.mark.skip(reason="Skip until PermissionError is fixed")
@pytest.mark.parametrize(
    "test_input_split,test_input_exercise",
    [("legs", "squat")],  # , ('chest', 'pullover')],
)
def test_get_df(test_input_split, test_input_exercise):
    """Verify that dataframe has more than 2 entries."""
    table_2021, _ = setup()
    df = get_df(table_2021, test_input_split, test_input_exercise)
    assert len(df) > 2


@pytest.mark.skip(reason="Skip until PermissionError is fixed")
def test_one_rep_max_estimator():
    """Verify that 1RM has progression."""

    table_2021, table_2022 = setup()

    df_2021 = get_df(table_2021, "legs", "squat")
    df_1rm_2021 = one_rep_max_estimator(df_2021)

    df_2022 = get_df(table_2022, "legs", "squat")
    df_1rm_2022 = one_rep_max_estimator(df_2022)

    value_2021 = df_1rm_2021.loc["2021-12-11", "1RM"]
    value_2022 = df_1rm_2022.loc["2022-03-14", "1RM"]

    print(value_2021, value_2022)

    # Check that for program_1, first squat 1RM is less or equal to 1RM of last squat
    # if pd.isna(value_2021) or pd.isna(value_2022):
    #     print("One of the values is NaN, comparison not possible.")
    # else:
    assert value_2021 <= value_2022


@pytest.mark.skip(reason="Skip until PermissionError is fixed")
def test_get_data():
    """Verify that the correct lists (timestamps and 1RM estimates) are returned,
    for real training data from program_1
    """

    table_2021, _ = setup()

    df = get_df(table_2021, "legs", "squat")
    df_1rm = one_rep_max_estimator(df)
    x, y = get_data(df_1rm)

    real_x_program_1 = [
        1639177200.0,
        1640386800.0,
    ]
    real_y_program_1 = [
        102.86,
        91.43,
    ]

    # TODO:
    assert x[:10] == real_x_program_1
    assert y[:10] == real_y_program_1
