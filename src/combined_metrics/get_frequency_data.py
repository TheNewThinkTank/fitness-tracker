"""
Prepare workout frequency data for plotting.
"""

import pandas as pd  # type: ignore
from datetime_tools.get_year_and_week import get_year_and_week  # type: ignore


def get_frequency_data(table, year_to_plot: str) -> pd.DataFrame:
    """Get workout frequency data for plotting.

    :param table: TinyDB table
    :type table: TinyDB.table
    :param year_to_plot: year to plot
    :type year_to_plot: str
    :return: workout frequency data
    :rtype: pd.DataFrame
    """

    df = pd.DataFrame()
    for item in table:

        if not item["date"].startswith(year_to_plot):
            continue

        year, week = get_year_and_week(item["date"])

        df_tmp = pd.DataFrame(
            {"year": year,
             "week": week,
             "workouts": 0
             },
            index=[0]
            )
        df = pd.concat(
            [df, df_tmp],
            ignore_index=True,
        )
    res = df.groupby(["year", "week"]).size()
    res_df = res.to_frame(name="workouts").reset_index()
    res_df["date"] = pd.to_datetime(
        res_df.assign(day=1, month=1)[["year", "month", "day"]]
    ) + pd.to_timedelta(res_df.week * 7, unit="days")

    return res_df
