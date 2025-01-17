"""
Plot weight-training data with fit.
"""

import argparse
from datetime import datetime
import matplotlib.pyplot as plt  # type: ignore
import seaborn as sns  # type: ignore
from src.model.model import (  # type: ignore
    get_data,
    get_df,
    one_rep_max_estimator,
    calc_volume
)
from src.utils.set_db_and_table import set_db_and_table  # type: ignore
from src.utils.config_loader import ConfigLoader  # type: ignore

config = ConfigLoader.load_config()
IMG_PATH = config["img_path"]


def create_1rm_plots(datatype: str, x: list, y: list, exercise: str) -> None:
    """Plot training data 1RM with fit.

    :param datatype: Data type: real or simulated
    :type datatype: str
    :param x: x-axis data
    :type x: list
    :param y: y-axis data
    :type y: list
    :param exercise: Exercise name
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

    plt.savefig(
        f"{IMG_PATH}all_years/one_rep_max/{datatype}_fitted_data_{exercise}_splines.png"
        )

    plt.clf()  # clear figure before next plot


def create_volume_plots(datatype: str, x: list, y: list, exercise: str) -> None:
    """Create volume plots.

    :param datatype: Data type: real or simulated
    :type datatype: str
    :param x: x-axis data
    :type x: list
    :param y: y-axis data
    :type y: list
    :param exercise: Exercise name
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
    plt.savefig(
        f"{IMG_PATH}all_years/volume/{datatype}_fitted_data_{exercise}_gvt.png"
        )
    plt.clf()  # clear figure before next plot


# TODO: unit test below function
def get_split(pgm: str) -> list[tuple[list, str]]:
    """Get split and key exercises.

    :param pgm: Program type: 1rm or gvt
    :type pgm: str
    :return: Split and key exercises
    :rtype: list[tuple[list, str]]
    """

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


def make_plots(
        pgm: str,
        split_selection: list[tuple[list, str]],
        table,
        datatype: str
        ) -> None:
    """Make plots.

    :param pgm: Program type
    :type pgm: str
    :param split_selection: Split and key exercises
    :type split_selection: list[tuple[list, str]]
    :param table: TinyDB table
    :type table: TinyDB.table
    :param datatype: Data type: real or simulated
    :type datatype: str
    :raises ValueError: If program type is not 1rm or gvt
    """

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
    """Get data and create figure.
    """

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
