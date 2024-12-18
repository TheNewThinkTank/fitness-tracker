"""
Date: 2021-12-27
Purpose: Plot weight-training data with fit
"""

__author__ = "Gustav Collin Rasmussen"
__version__ = "0.1.0"

import argparse
import os
import sys
from datetime import datetime
# from pprint import pprint as pp
import matplotlib.pyplot as plt  # type: ignore
import seaborn as sns  # type: ignore
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from model import get_data, get_df, one_rep_max_estimator, calc_volume  # type: ignore
from utils.set_db_and_table import set_db_and_table  # type: ignore

IMG_PATH = './docs/project_docs/img/'


def create_1rm_plots(datatype: str, x: list, y: list, exercise: str) -> None:
    """Plot training data 1RM with fit

    :param datatype: _description_
    :type datatype: str
    :param x: _description_
    :type x: list
    :param y: _description_
    :type y: list
    :param exercise: _description_
    :type exercise: str
    """

    plt.figure(figsize=(8, 8))

    x_prg1, x_prg2 = x[:10], x[10:]
    y_prg1, y_prg2 = y[:10], y[10:]

    # Only add confidence intervals if there are sufficient data points
    if len(x) < 5:
        sns.set_theme()
        ax = sns.scatterplot(x=x, y=y)
        ax.set_title(f"{exercise}")
    else:
        # ax = sns.regplot(x=x, y=y, ci=68, truncate=False)
        ax = sns.regplot(
            x=x_prg1, y=y_prg1, ci=68, truncate=False, label="Program 1: 4-split"
        )
        sns.regplot(x=x_prg2, y=y_prg2, ci=68, truncate=True, label="Program 2: PPL")
        ax.set_title(f"{exercise}", fontsize=30)

    xticks = ax.get_xticks()
    xticks_dates = [datetime.fromtimestamp(x).strftime("%Y-%m-%d") for x in xticks]

    ax.set_xticklabels(xticks_dates)
    plt.ylim(0, max(y) + 5)
    plt.xticks(rotation=45)
    ax.set_ylabel("1 RM estimates [kg]", fontsize=20)
    ax.legend(loc="lower right", fontsize=20)
    plt.savefig(f"{IMG_PATH}{datatype}_fitted_data_{exercise}_splines.png")
    plt.clf()  # clear figure before next plot


def create_volume_plots(datatype: str, x: list, y: list, exercise: str) -> None:
    """_summary_

    :param datatype: _description_
    :type datatype: str
    :param x: _description_
    :type x: list
    :param y: _description_
    :type y: list
    :param exercise: _description_
    :type exercise: str
    """

    plt.figure(figsize=(8, 8))

    # TODO: lookup dates and use get_program instead of list slicing
    x_prg1, x_prg2, x_prg3 = x[:10], x[10:20], x[20:]
    y_prg1, y_prg2, y_prg3 = y[:10], y[10:20], y[20:]

    ax = sns.regplot(x=x_prg1, y=y_prg1, ci=68, label="Program 1: 4-SPLIT")
    sns.regplot(x=x_prg2, y=y_prg2, ci=68, label="Program 2: PPL")
    sns.regplot(x=x_prg3, y=y_prg3, ci=68, label="Program 3: GVT")

    ax.set_title(f"{exercise}", fontsize=30)
    xticks = ax.get_xticks()
    xticks_dates = [datetime.fromtimestamp(x).strftime("%Y-%m-%d") for x in xticks]
    ax.set_xticklabels(xticks_dates)
    plt.ylim(0, max(y) + 5)
    plt.xticks(rotation=45)
    ax.set_ylabel("Volume [kg]", fontsize=20)
    ax.legend(loc="lower right", fontsize=20)
    plt.savefig(f"{IMG_PATH}{datatype}_fitted_data_{exercise}_gvt.png")
    plt.clf()  # clear figure before next plot


def get_split(pgm: str) -> list[tuple[list, str]]:

    splits_and_key_exercises_1rm = [
        (["chest", "push"], "bb_bench_press"),
        (["back", "pull"], "seated_row"),
        (["legs"], "squat"),
        (["legs"], "deadlift"),
    ]

    splits_and_key_exercises_gvt = [
        (["chest", "push", "chest_and_back"], "bb_bench_press"),
        (["legs", "legs_and_abs"], "squat"),
    ]

    split_selector = {
        "1rm": splits_and_key_exercises_1rm,
        "gvt": splits_and_key_exercises_gvt,
    }

    return split_selector[pgm]


def make_plots(pgm, split_selection, table, datatype):

    for splits, exercise in split_selection:
        df = get_df(table, splits, exercise)

        match pgm:
            case "1rm":
                df_plot = one_rep_max_estimator(df)
                x, y = get_data(df_plot)
                create_1rm_plots(datatype, x, y, exercise)
            case "gvt":
                df_plot = calc_volume(df)
                x, y = get_data(df_plot, y_col="volume")
                create_volume_plots(datatype, x, y, exercise)
            case _:
                raise ValueError


def main() -> None:
    """Get data and create figure."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--datatype", type=str, required=True)  # real/simulated
    parser.add_argument("--pgm", type=str, required=True)  # 1rm/gvt
    args = parser.parse_args()
    datatype = args.datatype
    pgm = args.pgm
    _, table, _ = set_db_and_table(datatype)

    split_selection = get_split(pgm)

    make_plots(pgm, split_selection, table, datatype)


if __name__ == "__main__":
    main()
