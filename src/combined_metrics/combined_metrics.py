"""
Date: 2022-09-16
Purpose: read workout data and calculate combined metrics.
"""

__author__ = "Gustav Collin Rasmussen"
__version__ = "0.1.0"

from datetime import datetime as dt
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import matplotlib.pyplot as plt  # type: ignore
import matplotlib.dates as mdates  # type: ignore
import pandas as pd  # type: ignore
import seaborn as sns  # type: ignore

from helpers.set_db_and_table import set_db_and_table  # type: ignore
from helpers.get_year_and_week import get_year_and_week  # type: ignore
from helpers.get_workout_duration import get_all_durations  # type: ignore
from helpers.get_bodyweight import get_bw  # type: ignore

from model.model import get_data, one_rep_max_estimator, get_df  # type: ignore


def get_total_volume(table) -> list[tuple[str, int]]:
    """_summary_

    :param table: _description_
    :type table: _type_
    :return: _description_
    :rtype: list[tuple[str, int]]
    """

    bodyweight = str(get_bw())  # "80"
    date_and_volume = []
    for item in table:
        total_volume = 0

        for exercise in item["exercises"].keys():
            number_of_sets = len(item["exercises"][exercise])
            volume_partial = []
            for s in item["exercises"][exercise]:
                if s["weight"][:-3] != "0":

                    weight = eval(s["weight"][:-3].replace("BODYWEIGHT", bodyweight))

                    volume_partial.append(s["reps"] * weight)
                else:
                    volume_partial.append(s["reps"] * 1)
            total_volume += number_of_sets * max(volume_partial)

        date_and_volume.append((item["date"], total_volume))
    return date_and_volume


def plot_frequency(table):
    """_summary_

    :param table: _description_
    :type table: _type_
    """

    df = pd.DataFrame()
    for item in table:
        year, week = get_year_and_week(item["date"])
        df_tmp = pd.DataFrame({"year": year, "week": week, "workouts": 0}, index=[0])
        df = pd.concat(
            [df, df_tmp],
            ignore_index=True,
        )
    res = df.groupby(["year", "week"]).size()
    res_df = res.to_frame(name="workouts").reset_index()
    print(res_df)
    res_df["date"] = pd.to_datetime(
        res_df.assign(day=1, month=1)[["year", "month", "day"]]
    ) + pd.to_timedelta(res_df.week * 7, unit="days")
    # print(res_df)

    fig, ax = plt.subplots()
    # plt.style.use("seaborn-v0_8")
    res_df.plot(x="date", y="workouts", marker="o", ax=ax)
    # bar = sns.barplot(data=res_df, x="date", y="workouts", ax=ax)

    freq_format = mdates.DateFormatter("%Y week %U")
    ax.xaxis.set_major_formatter(freq_format)
    ax.get_legend().remove()
    plt.yticks(res_df["workouts"], res_df["workouts"])

    # ax.bar(res_df["date"], res_df["workouts"])
    # sns.barplot(data=res_df, x="date", y="workouts")
    # plt.xticks(res_df["date"], rotation=90)

    # for item in bar.get_xticklabels():
    #     item.set_rotation(45)
    # plt.xticks(rotation=70)

    # plt.plot_date(res_df["date"], res_df["workouts"], linestyle="solid")
    # plt.gcf().autofmt_xdate()
    # plt.tight_layout()
    # sns.histplot(data=res_df, x="week", y="workouts", binwidth=1, kde=True, hue="year")

    plt.title("Workout Frequency", fontsize=20)
    plt.xlabel("workout week", fontsize=15)
    plt.ylabel("weekly workouts", fontsize=15)
    plt.grid()
    plt.savefig("img/workout_frequency.png")
    # plt.show()
    plt.clf()


def plot_duration(table):
    """_summary_

    :param table: _description_
    :type table: _type_
    """

    date_and_duration = get_all_durations()
    date_and_volume = get_total_volume(table)
    volumes = [d_v[1] for d_v in date_and_volume if d_v[0] in date_and_duration.keys()]
    date_and_duration = {
        dt.strptime(k, "%Y-%m-%d").date(): v for k, v in date_and_duration.items()
    }
    dates = list(date_and_duration.keys())
    durations = list(date_and_duration.values())

    norm = plt.Normalize(min(volumes), max(volumes))
    sm = plt.cm.ScalarMappable(cmap="Reds", norm=norm)
    sm.set_array([])

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    ax = sns.scatterplot(x=dates, y=durations, hue=volumes, palette="Reds", s=100)
    plt.plot(dates, durations, zorder=0, c="brown")
    plt.gcf().autofmt_xdate()

    ax.get_legend().remove()
    ax.figure.colorbar(sm)

    plt.grid()
    plt.xlabel("workout date", fontsize=15)
    plt.ylabel("duration [minutes]", fontsize=15)
    plt.title("Duration and total volume [kg]", fontsize=20)
    plt.xticks(dates, dates)

    # plt.show()
    plt.savefig("img/workout_duration.png")
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
    plt.savefig(f"img/workout_duration_volume_1rm_{EXERCISE}.png")
    plt.clf()


def main() -> None:
    """_summary_
    """

    datatype = "real"
    _, table, _ = set_db_and_table(datatype)

    plot_frequency(table)
    plot_duration(table)
    plot_duration_volume_1rm(table)


if __name__ == "__main__":
    main()
