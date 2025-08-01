"""
Read workout data and calculate combined metrics.
"""

from datetime import datetime as dt
from src.utils.config import settings  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import matplotlib.dates as mdates  # type: ignore
import matplotlib.cm as cm  # type: ignore
import matplotlib.colors as mcolors  # type: ignore
from matplotlib.ticker import MaxNLocator  # type: ignore
import pandas as pd  # type: ignore
from pprint import pformat  # type: ignore
from loguru import logger  # type: ignore
import seaborn as sns  # type: ignore
from typing import Any  # type: ignore
# import statsmodels.api as sm  # type: ignore
# from scipy.interpolate import make_interp_spline  # type: ignore
# from icecream import ic  # type: ignore
from src.utils.set_db_and_table import set_db_and_table  # type: ignore
from src.utils.get_workout_duration import get_all_durations  # type: ignore
from src.utils.get_volume import get_total_volume  # type: ignore
from datetime_tools.lookup import get_year_and_month  # type: ignore
from src.model.model import one_rep_max_estimator, get_df  # type: ignore
from src.combined_metrics.get_frequency_data import get_frequency_data  # type: ignore


def save_plot(fig, path) -> None:
    """Save the plot to the specified path."""
    fig.tight_layout()
    fig.subplots_adjust(top=0.85, bottom=0.2)
    fig.savefig(path, bbox_inches='tight')
    plt.clf()


def configure_plot(ax, x_ticks, x_label, y_label, title) -> None:
    """Configure plot settings."""
    ax.set_xlabel(x_label, fontsize=15)
    ax.set_ylabel(y_label, fontsize=15)
    ax.set_title(title, fontsize=20)
    ax.grid(True)
    plt.xticks(x_ticks, rotation=45, ha='right')


def plot_frequency(table, year_to_plot: str) -> None:
    """Plot workout frequency.

    :param table: TinyDB table
    :type table: TinyDB.table
    :param year_to_plot: year to plot
    :type year_to_plot: str
    :return: None
    """

    res_df = get_frequency_data(table, year_to_plot)

    # Ensure date values are properly converted to datetime objects
    res_df['date'] = pd.to_datetime(res_df['date'], errors='coerce')
    res_df = res_df.dropna(subset=['date'])  # Drop rows with invalid dates

    logger.debug("Date range after conversion:")
    logger.debug(f"{res_df['date'].min()}, {res_df['date'].max()}")

    if res_df.empty:
        logger.error(f"No valid data to plot for the year {year_to_plot}.")
        return

    fig, ax = plt.subplots(figsize=(10, 6))

    # lowess (locally weighted scatterplot smoothing)
    # Apply lowess smoothing
    # lowess = sm.nonparametric.lowess
    # smoothed = lowess(res_df['workouts'], res_df['date'].astype('int64') // 10**9, frac=0.1)
    # smoothed = lowess(res_df['workouts'], res_df['date'], frac=0.1)
    # Convert smoothed dates back to datetime objects
    # smoothed_dates = pd.to_datetime(smoothed[:, 0], unit='s')
    # logger.debug(pformat(smoothed))
    # if smoothed.size == 0:
    #     logger.error("Lowess smoothing failed. Not enough data points.")
    #     return
    # Plot the smoothed curve
    # ax.plot(smoothed_dates, smoothed[:, 1], color="#6c8ebf", label="Smoothed Curve")
    # ax.plot(smoothed[:, 0], smoothed[:, 1], color="#6c8ebf", label="Smoothed Curve")

    # Apply cubic spline interpolation for smoother curves
    # x = res_df['date'].astype('int64') // 10**9  # Convert dates to seconds since epoch
    # y = res_df['workouts']
    # spline = make_interp_spline(x, y, k=3)  # Cubic spline interpolation
    # x_smooth = pd.date_range(start=res_df['date'].min(), end=res_df['date'].max(), freq='D')
    # y_smooth = spline(x_smooth.astype('int64') // 10**9)

    # Plot the smoothed curve
    # ax.plot(x_smooth, y_smooth, color="#6c8ebf", label="Smoothed Curve")

    logger.info("res_df:")
    logger.info(pformat(res_df.head()))
    logger.info(pformat(res_df))
    logger.info(f"Dates range: {res_df['date'].min()} to {res_df['date'].max()}")

    # sns.barplot(
    #     x="date", 
    #     y="workouts", 
    #     data=res_df, 
    #     ax=ax, 
    #     color="#6c8ebf",
    #     label="Data Points"
    # )

    sns.scatterplot(
        x="date", 
        y="workouts", 
        data=res_df, 
        ax=ax, 
        color="#6c8ebf",
        marker="o",
        s=100,
        label="Data Points"
    )

    # sns.lineplot(
    #     x="date", 
    #     y="workouts", 
    #     marker="o", 
    #     data=res_df, 
    #     ax=ax, 
    #     color="#6c8ebf"
    # )
    # ax.plot(res_df['date'], res_df['workouts'], marker='o', linestyle='-', color='b')

    # Ensure the x-axis limits are within the date range
    ax.set_xlim(res_df['date'].min(), res_df['date'].max())

    if len(res_df['date'].unique()) < 7:  # If fewer than a week of data points
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))  # Use simple integer ticks
    else:
        ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    # ax.xaxis.set_major_locator(mdates.WeekdayLocator())

    date_format = "%Y week %U"  # "%Y-%m-%d"
    ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))

    ax.set_ylim(bottom=0)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    configure_plot(
        ax,
        res_df['date'],
        "Workout Week",
        "Weekly Workouts",
        f"{year_to_plot} Workout Frequency"
        )

    legend = ax.get_legend()
    if legend is not None:
        legend.remove()

    # plt.show()
    save_path = f"{settings['IMG_PATH']}{year_to_plot}/{year_to_plot}_workout_frequency.png"
    save_plot(fig, save_path)


def plot_duration(table, year_to_plot: str, month_to_plot: str) -> None:
    """Plot workout duration.

    :param table: TinyDB table
    :type table: TinyDB.table
    :param year_to_plot: year to plot
    :type year_to_plot: str
    :param month_to_plot: month to plot
    :type month_to_plot: str
    :return: None
    """

    _date_and_duration = get_all_durations(year_to_plot)

    date_and_duration = {
        date: duration
        for date, duration in _date_and_duration.items()
        if get_year_and_month(date) == (year_to_plot, month_to_plot)
    }

    logger.debug(pformat(date_and_duration))

    date_and_volume = get_total_volume(table)
    volumes = [d_v[1] for d_v in date_and_volume if d_v[0] in date_and_duration.keys()]

    date_and_duration = {
        dt.strptime(k, "%Y-%m-%d").date(): v for k, v in date_and_duration.items()
    }
    dates = list(date_and_duration.keys())
    durations = list(date_and_duration.values())

    norm = mcolors.Normalize(min(volumes), max(volumes))
    sm = cm.ScalarMappable(cmap="Reds", norm=norm)
    sm.set_array([])

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.xaxis.set_major_locator(mdates.DayLocator())

    # TODO: start y-axis at zero
    sns.scatterplot(x=dates, y=durations, hue=volumes, palette="Reds", s=100, ax=ax)
    plt.plot(dates, durations, zorder=0, c="brown")
    ax.set_ylim(bottom=0)

    legend = ax.get_legend()
    if legend is not None:
        legend.remove()
    plt.colorbar(sm, ax=ax)

    configure_plot(
        ax,
        dates,
        "Workout Date",
        "Duration [minutes]",
        f"Duration and Total Volume [kg] ({month_to_plot} {year_to_plot})"
        )

    # plt.show()
    save_path = f"{settings['IMG_PATH']}{year_to_plot}/workout_duration_{month_to_plot}_{year_to_plot}.png"
    save_plot(fig, save_path)


def plot_duration_volume_1rm(table, year_to_plot: str) -> None:
    """Plot workout duration, volume and 1RM.

    :param table: TinyDB table
    :type table: TinyDB.table
    :return: None
    """

    _date_and_duration = get_all_durations(year_to_plot)
    date_and_volume = get_total_volume(table)
    _dates = _date_and_duration.keys()
    splits = [
        "push",
        "full_body",
        # "legs",
        # "legs_and_abs",
    ]
    exercise = "bb_bench_press"  # "squat"
    df = get_df(table, splits=splits, exercise=exercise)
    one_rm = one_rep_max_estimator(df)
    one_rm_filtered = one_rm[one_rm.index.isin(_dates)]
    volumes = [
        d_v[1] for d_v in date_and_volume if d_v[0] in one_rm_filtered.index  # dates
    ]

    date_and_duration: dict[Any, Any] = {
        dt.strptime(k, "%Y-%m-%d").date(): v
        for k, v in _date_and_duration.items()
        if k in one_rm_filtered.index
    }

    dates: list[Any] = list(date_and_duration.keys())
    durations = list(date_and_duration.values())
    # one_rm_values = one_rm_filtered["1RM"].to_list()

    norm = mcolors.Normalize(min(volumes), max(volumes))
    sm = plt.cm.ScalarMappable(cmap="Reds", norm=norm)
    sm.set_array([])

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.xaxis.set_major_locator(mdates.DayLocator())

    sns.scatterplot(
        x=dates, y=durations, hue=volumes, palette="Reds", s=one_rm, ax=ax
        )
    plt.plot(dates, durations, zorder=0, c="brown")

    legend = ax.get_legend()
    if legend is not None:
        legend.remove()

    plt.colorbar(sm, ax=ax)

    configure_plot(
        ax,
        dates,
        "Workout Date",
        "Duration [minutes]",
        f"Duration, Volume, 1RM ({exercise})"
        )

    save_path = f"{settings['IMG_PATH']}all_years/workout_duration_volume_1rm_{exercise}.png"
    save_plot(fig, save_path)


def main() -> None:
    """Main function to run the script.
    """

    import argparse
    import calendar

    default_month = calendar.month_name[1]

    # years = [
    #     '2021',
    #     '2022',
    #     '2023',
    #     '2024',
    #     '2025',
    #     ]

    parser = argparse.ArgumentParser(
        description="Get combined metrics for volume and frequency of workouts.",
    )

    parser.add_argument(
        "-y",
        "--year_to_plot",
        type=str,
        default='2025',
        )

    parser.add_argument(
        "-m",
        "--month_to_plot",
        type=str,
        default=default_month
        )

    parser.add_argument(
        "-t",
        "--datatype",
        type=str,
        default="real",
        help="Either real or simulated workout data.",
        )

    args = parser.parse_args()

    datatype = args.datatype
    year_to_plot = args.year_to_plot
    month_to_plot = args.month_to_plot

    _, table, _ = set_db_and_table(datatype, year=int(year_to_plot))

    logger.debug(default_month)

    plot_frequency(table, year_to_plot)
    plot_duration(table, year_to_plot, month_to_plot)
    # plot_duration_volume_1rm(table, year_to_plot)


if __name__ == "__main__":
    main()
