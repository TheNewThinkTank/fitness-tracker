
import pytest
import sys
import logging
import pandas as pd
from tinydb import TinyDB
from tinydb.storages import MemoryStorage
from src.model.model import (  # type: ignore
    get_df,
    get_weight,
    calc_volume,
    one_rep_max_estimator,
    get_data,
    main,
)


# Fixture for creating a mock TinyDB table
@pytest.fixture
def mock_table():
    db = TinyDB(storage=MemoryStorage)
    table = db.table("workouts")
    table.insert(
        {
            "date": "2023-10-01",
            "split": "chest",
            "exercises": {
                "barbell_bench_press": [
                    {"set_number": 1, "reps": 10, "weight": "100 kg"},
                    {"set_number": 2, "reps": 8, "weight": "110 kg"},
                ]
            },
        }
    )
    table.insert(
        {
            "date": "2023-10-02",
            "split": "push",
            "exercises": {
                "barbell_bench_press": [
                    {"set_number": 1, "reps": 12, "weight": "95 kg"},
                    {"set_number": 2, "reps": 10, "weight": "105 kg"},
                ]
            },
        }
    )
    return table


def test_get_df(mock_table):
    splits = ["chest", "push"]
    exercise = "barbell_bench_press"
    df = get_df(mock_table, splits=splits, exercise=exercise)
    
    # Check that the DataFrame is not empty
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    
    # Check that the DataFrame contains the correct exercise
    assert "barbell_bench_press" in mock_table.all()[0]["exercises"].keys()
    
    # Check that the DataFrame contains the correct dates
    expected_dates = {"2023-10-01", "2023-10-02"}
    assert set(df["date"].unique()) == expected_dates
    
    # Check that the DataFrame contains the correct columns
    expected_columns = {"set_number", "reps", "weight", "date"}
    assert set(df.columns) == expected_columns


# Test get_weight function
def test_get_weight():
    data = {"weight": ["100 kg", "110 kg", "120 kg"]}
    df = pd.DataFrame(data)
    weights = get_weight(df)

    assert isinstance(weights, pd.Series)
    assert all(isinstance(w, float) for w in weights)


# Test calc_volume function
def test_calc_volume():
    data = {
        "date": ["2023-10-01", "2023-10-01", "2023-10-02"],
        "set_number": [1, 2, 1],
        "reps": [10, 8, 12],
        "weight": ["100 kg", "110 kg", "95 kg"],
    }
    df = pd.DataFrame(data)
    volume_df = calc_volume(df)

    assert isinstance(volume_df, pd.DataFrame)
    assert "volume" in volume_df.columns
    assert not volume_df.empty


# Test one_rep_max_estimator function
def test_one_rep_max_estimator():
    data = {
        "date": ["2023-10-01", "2023-10-01", "2023-10-02"],
        "set_number": [1, 2, 1],
        "reps": [10, 8, 12],
        "weight": ["100 kg", "110 kg", "95 kg"],
    }
    df = pd.DataFrame(data)

    for formula in ["acsm", "epley", "brzycki"]:
        one_rm_df = one_rep_max_estimator(df, formula=formula)
        assert isinstance(one_rm_df, pd.DataFrame)
        assert "1RM" in one_rm_df.columns
        assert not one_rm_df.empty


# Test get_data function
def test_get_data():
    data = {
        "date": ["2023-10-01", "2023-10-02"],
        "1RM": [120.5, 130.75],
        "volume": [1200, 1300],
    }
    df = pd.DataFrame(data).set_index("date")

    x, y = get_data(df, y_col="1RM")
    assert isinstance(x, list)
    assert isinstance(y, list)
    assert len(x) == len(y)

    x, y = get_data(df, y_col="volume")
    assert isinstance(x, list)
    assert isinstance(y, list)
    assert len(x) == len(y)


# # Test main function (integration test)
# def test_main(capsys):
#     # Redirect logging output to stdout
#     logger = logging.getLogger()
#     logger.setLevel(logging.INFO)
#     stream_handler = logging.StreamHandler(sys.stdout)
#     logger.addHandler(stream_handler)
    
#     # Call the main function
#     main()
    
#     # Capture the output
#     captured = capsys.readouterr()
    
#     # Check if logs are printed
#     assert "Exercise: squat" in captured.out
#     assert "Workout timestamps:" in captured.out
#     assert "1 RM estimates:" in captured.out
#     assert "Volume:" in captured.out
    
#     # Clean up the logger to avoid affecting other tests
#     logger.removeHandler(stream_handler)


# Test invalid formula in one_rep_max_estimator
def test_invalid_formula():
    data = {
        "date": ["2023-10-01", "2023-10-01", "2023-10-02"],
        "set_number": [1, 2, 1],
        "reps": [10, 8, 12],
        "weight": ["100 kg", "110 kg", "95 kg"],
    }
    df = pd.DataFrame(data)

    with pytest.raises(SystemExit):
        one_rep_max_estimator(df, formula="invalid_formula")


# Test invalid y_col in get_data
def test_invalid_y_col():
    data = {
        "date": ["2023-10-01", "2023-10-02"],
        "1RM": [120.5, 130.75],
        "volume": [1200, 1300],
    }
    df = pd.DataFrame(data).set_index("date")

    with pytest.raises(ValueError):
        get_data(df, y_col="invalid_column")
