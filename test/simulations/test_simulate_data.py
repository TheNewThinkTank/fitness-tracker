
from datetime import datetime, timedelta
from src.simulations.simulate_data import (  # type: ignore
    reservoir_sample,
    get_dates
)


def test_reservoir_sample():
    elements = ["a", "b", "c", "d", "e"]
    generator = (x for x in elements)
    sample_size = 3
    
    sample = reservoir_sample(generator, sample_size)
    
    assert len(sample) == sample_size, "Sample size does not match the expected size."
    assert len(set(sample)) == sample_size, "Sample contains duplicate elements."
    assert all(x in elements for x in sample), "Sample contains elements not in the original generator."


def test_get_dates():
    number_of_workouts = 3
    start_date = datetime(2020, 1, 1)
    periods = 10
    
    dates = get_dates(number_of_workouts, start_date, periods)
    
    assert len(dates) == number_of_workouts, "Number of dates does not match the expected number."
    assert len(set(dates)) == number_of_workouts, "Dates contain duplicates."
    
    for date_str in dates:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        assert start_date <= date <= start_date + timedelta(days=periods-1), "Date is out of expected range."


def test_get_dates_sorted():
    number_of_workouts = 5
    start_date = datetime(2020, 1, 1)
    periods = 365
    
    dates = get_dates(number_of_workouts, start_date, periods)
    dates_sorted = sorted(dates)
    
    # Check that the sorted list is actually sorted
    assert dates_sorted == sorted(dates_sorted), "The dates are not sorted in ascending order."
