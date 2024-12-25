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


def plot_frequency(table, year_to_plot: str) -> None:
    """_summary_

    :param table: _description_
    :type table: _type_
    """

    res_df = get_frequency_data(table, year_to_plot)
    # res_df['date'] = pd.to_datetime(res_df['date'])
    # ic(res_df)

    _, ax = plt.subplots()

    ax.plot(res_df['date'], res_df['workouts'], marker='o', linestyle='-', color='b')
    # ax = sns.scatterplot(x=res_df['date'], y=res_df['workouts'])  # , palette="Reds", s=100)

    ax.xaxis.set_major_locator(mdates.WeekdayLocator())  # mdates.AutoDateLocator()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y week %U"))

    ticks = [res_df['date'].iloc[i] for i in range(len(res_df['date']))]

    plt.xticks(ticks, rotation=45, ha='right')
    # plt.xticks(rotation=45, ha='right')

    # ax.get_legend().remove()
    plt.yticks(res_df["workouts"], res_df["workouts"])
    plt.xlabel("workout week", fontsize=15)
    plt.ylabel("weekly workouts", fontsize=15)
    plt.grid(True)
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    # Adjust x-axis limits to shift data points to the left
    plt.xlim(res_df['date'].iloc[0] - pd.to_timedelta(3, unit='d'),
             res_df['date'].iloc[-1] + pd.to_timedelta(3, unit='d')
             )
    plt.title(f"{year_to_plot} Workout Frequency", fontsize=20)
    plt.savefig(f"{IMG_PATH}{year_to_plot}_workout_frequency.png")
    # plt.show()
    plt.clf()


def plot_duration(table, year_to_plot: str, month_to_plot: str) -> None:
    """_summary_

    :param table: _description_
    :type table: _type_
    :param year_to_plot: _description_
    :type year_to_plot: str
    :param month_to_plot: _description_
    :type month_to_plot: str
    """

    _date_and_duration = get_all_durations(year_to_plot)
    # ic(_date_and_duration)
    # pp(_date_and_duration)
    date_and_duration = dict()
    for date, duration in _date_and_duration.items():
        YEAR, MONTH = get_year_and_month(date)
        if YEAR == year_to_plot and MONTH == month_to_plot:
            # print(YEAR, MONTH)
            date_and_duration[date] = duration
    pp(date_and_duration)

    date_and_volume = get_total_volume(table)

    # ic(date_and_volume)
    # ic(date_and_duration)

    volumes = [d_v[1] for d_v in date_and_volume if d_v[0] in date_and_duration.keys()]

    date_and_duration = {
        dt.strptime(k, "%Y-%m-%d").date(): v for k, v in date_and_duration.items()
    }
    dates = list(date_and_duration.keys())
    durations = list(date_and_duration.values())

    # ic(dates)
    # ic(durations)
    # ic(volumes)

    # pp(date_and_duration)
    # pp(date_and_volume)

    norm = mcolors.Normalize(min(volumes), max(volumes))
    sm = cm.ScalarMappable(cmap="Reds", norm=norm)
    sm.set_array([])

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())

    ax = sns.scatterplot(x=dates, y=durations, hue=volumes, palette="Reds", s=100)
    plt.plot(dates, durations, zorder=0, c="brown")
    plt.gcf().autofmt_xdate()

    ax.get_legend().remove()

    plt.colorbar(sm, ax=ax)

    plt.grid()
    plt.xlabel("workout date", fontsize=15)
    plt.ylabel("duration [minutes]", fontsize=15)
    plt.title(f"Duration and total volume [kg] ({month_to_plot} {year_to_plot})", fontsize=17)
    plt.xticks(dates, dates)

    # plt.show()
    plt.savefig(f"{IMG_PATH}workout_duration_{month_to_plot}_{year_to_plot}.png")
    plt.clf()


def plot_duration_volume_1rm(table):
    """_summary_

    :param table: _description_
    :type table: _type_
    """

    date_and_duration = get_all_durations()
    date_and_volume = get_total_volume(table)
    dates = date_and_duration.keys()
    _SPLITS = [
        "push",
        "full_body",
        # "legs",
        # "legs_and_abs",
    ]
    EXERCISE = "bb_bench_press"  # "squat"
    df = get_df(table, splits=_SPLITS, exercise=EXERCISE)
    one_rm = one_rep_max_estimator(df)
    one_rm_squat = one_rm[one_rm.index.isin(dates)]
    volumes = [
        d_v[1] for d_v in date_and_volume if d_v[0] in one_rm_squat.index  # dates
    ]

    date_and_duration = {
        dt.strptime(k, "%Y-%m-%d").date(): v
        for k, v in date_and_duration.items()
        if k in one_rm_squat.index
    }
    dates = list(date_and_duration.keys())
    durations = list(date_and_duration.values())
    one_rm = one_rm_squat["1RM"].to_list()

    print(dates)
    print(durations)
    print(one_rm)
    print(volumes)

    norm = plt.Normalize(min(volumes), max(volumes))
    sm = plt.cm.ScalarMappable(cmap="Reds", norm=norm)
    sm.set_array([])

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    ax = sns.scatterplot(x=dates, y=durations, hue=volumes, palette="Reds", s=one_rm)
    plt.plot(dates, durations, zorder=0, c="brown")
    plt.gcf().autofmt_xdate()

    ax.get_legend().remove()
    ax.figure.colorbar(sm)

    plt.grid()
    plt.xlabel("workout date", fontsize=15)
    plt.ylabel("duration [minutes]", fontsize=15)
    plt.title(f"Duration, volume, 1RM ({EXERCISE})", fontsize=15)
    plt.xticks(dates, dates)

    # plt.show()
    plt.savefig(f"{IMG_PATH}workout_duration_volume_1rm_{EXERCISE}.png")
    plt.clf()


def main() -> None:
    """_summary_
    """

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--year_to_plot", type=str, default='2024')
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
