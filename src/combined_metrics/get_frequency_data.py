"""
Prepare workout frequency data for plotting.
"""

from collections import Counter
from datetime import date, timedelta

import pandas as pd  # type: ignore


def get_frequency_data(table, year_to_plot: str) -> pd.DataFrame:
    """Get workout frequency data for plotting.

    :param table: TinyDB table
    :type table: TinyDB.table
    :param year_to_plot: year to plot
    :type year_to_plot: str
    :return: workout frequency data
    :rtype: pd.DataFrame
    """

    counts: Counter[date] = Counter()
    for item in table:
        try:
            workout_date = date.fromisoformat(str(item["date"]))
        except (ValueError, KeyError, TypeError):
            continue
        if workout_date.year == int(year_to_plot):
            counts[workout_date - timedelta(days=workout_date.weekday())] += 1
    rows = []
    if counts:
        current = min(counts)
        while current <= max(counts):
            iso_year, week, _ = current.isocalendar()
            rows.append({"year": str(iso_year), "week": week, "workouts": counts[current], "date": pd.Timestamp(current)})
            current += timedelta(days=7)
    return pd.DataFrame(rows, columns=["year", "week", "workouts", "date"])
