"""
Read workout data and calculate combined metrics.
"""

from datetime import datetime as dt
import os
import sys
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
import matplotlib.pyplot as plt  # type: ignore
import matplotlib.dates as mdates  # type: ignore
import matplotlib.cm as cm  # type: ignore
import matplotlib.colors as mcolors  # type: ignore
import pandas as pd  # type: ignore
from pprint import pprint as pp
import seaborn as sns  # type: ignore
from icecream import ic  # type: ignore
from utils.set_db_and_table import set_db_and_table  # type: ignore
from utils.get_workout_duration import get_all_durations  # type: ignore
from utils.get_volume import get_total_volume  # type: ignore
from datetime_tools.lookup import get_year_and_month  # type: ignore
from model.model import one_rep_max_estimator, get_df  # type: ignore
from get_frequency_data import get_frequency_data  # type: ignore
from utils.config_loader import ConfigLoader  # type: ignore

config = ConfigLoader.load_config()
IMG_PATH = config["img_path"]


def save_plot(fig, path) -> None:
    """Save the plot to the specified path."""
    fig.tight_layout()
    fig.subplots_adjust(top=0.9)
    fig.savefig(path)
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
    fig, ax = plt.subplots()

    sns.lineplot(
        x="date", 
        y="workouts", 
        marker="o", 
        data=res_df, 
        ax=ax, 
        color="#6c8ebf"
    )
    # ax.plot(res_df['date'], res_df['workouts'], marker='o', linestyle='-', color='b')

    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y week %U"))

    configure_plot(
        ax,
        res_df['date'],
        "Workout Week",
        "Weekly Workouts",
        f"{year_to_plot} Workout Frequency"
        )

    save_path = f"{IMG_PATH}{year_to_plot}/{year_to_plot}_workout_frequency.png"
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

    pp(date_and_duration)

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

    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.xaxis.set_major_locator(mdates.DayLocator())

    sns.scatterplot(x=dates, y=durations, hue=volumes, palette="Reds", s=100, ax=ax)
    plt.plot(dates, durations, zorder=0, c="brown")

    ax.get_legend().remove()
    plt.colorbar(sm, ax=ax)

    configure_plot(
        ax,
        dates,
        "Workout Date",
        "Duration [minutes]",
        f"Duration and Total Volume [kg] ({month_to_plot} {year_to_plot})"
        )

    save_path = f"{IMG_PATH}{year_to_plot}/workout_duration_{month_to_plot}_{year_to_plot}.png"
    save_plot(fig, save_path)


def plot_duration_volume_1rm(table) -> None:
    """Plot workout duration, volume and 1RM.

    :param table: TinyDB table
    :type table: TinyDB.table
    :return: None
    """

    date_and_duration = get_all_durations()
    date_and_volume = get_total_volume(table)
    dates = date_and_duration.keys()
    splits = [
        "push",
        "full_body",
        # "legs",
        # "legs_and_abs",
    ]
    exercise = "bb_bench_press"  # "squat"
    df = get_df(table, splits=splits, exercise=exercise)
    one_rm = one_rep_max_estimator(df)
    one_rm_filtered = one_rm[one_rm.index.isin(dates)]
    volumes = [
        d_v[1] for d_v in date_and_volume if d_v[0] in one_rm_filtered.index  # dates
    ]

    date_and_duration = {
        dt.strptime(k, "%Y-%m-%d").date(): v
        for k, v in date_and_duration.items()
        if k in one_rm_filtered.index
    }
    dates = list(date_and_duration.keys())
    durations = list(date_and_duration.values())
    # one_rm_values = one_rm_filtered["1RM"].to_list()

    norm = mcolors.Normalize(min(volumes), max(volumes))
    sm = plt.cm.ScalarMappable(cmap="Reds", norm=norm)
    sm.set_array([])

    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.xaxis.set_major_locator(mdates.DayLocator())

    sns.scatterplot(x=dates, y=durations, hue=volumes, palette="Reds", s=one_rm, ax=ax)
    plt.plot(dates, durations, zorder=0, c="brown")

    ax.get_legend().remove()
    plt.colorbar(sm, ax=ax)

    configure_plot(
        ax,
        dates,
        "Workout Date",
        "Duration [minutes]",
        f"Duration, Volume, 1RM ({exercise})"
        )

    save_path = f"{IMG_PATH}all_years/workout_duration_volume_1rm_{exercise}.png"
    save_plot(fig, save_path)


def main() -> None:
    """Main function to run the script.
    """

    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--year_to_plot",
        type=str,
        default='2024'
        )

    parser.add_argument("--month_to_plot", type=str, default='December')
    parser.add_argument("--datatype", type=str, default="real")
    args = parser.parse_args()

    datatype = args.datatype
    year_to_plot = args.year_to_plot
    month_to_plot = args.month_to_plot

    _, table, _ = set_db_and_table(datatype, year=int(year_to_plot))

    plot_frequency(table, year_to_plot)
    plot_duration(table, year_to_plot, month_to_plot)
    # plot_duration_volume_1rm(table)


if __name__ == "__main__":
    main()
