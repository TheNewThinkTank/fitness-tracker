"""
Plot weight-training data with fit.
"""

import argparse
from datetime import datetime
from src.utils.config import settings  # type: ignore
from src.utils.get_program import get_pgm_from_date  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import seaborn as sns  # type: ignore
from src.model.model import (  # type: ignore
    get_data,
    get_df,
    one_rep_max_estimator,
    calc_volume
)
from src.utils.set_db_and_table import set_db_and_table  # type: ignore


def _split_by_program(x: list, y: list) -> list[tuple[list, list, str]]:
    """Group (x, y) timestamp pairs by their training program name.

    Returns a list of (x_group, y_group, program_name) tuples in order of first
    appearance.  Falls back to a single "Unknown" group when get_pgm_from_date
    returns None.
    """
    groups: dict[str, tuple[list, list]] = {}
    order: list[str] = []
    for xi, yi in zip(x, y):
        date_str = datetime.fromtimestamp(xi).strftime("%Y-%m-%d")
        pgm = get_pgm_from_date(date_str) or "Unknown"
        if pgm not in groups:
            groups[pgm] = ([], [])
            order.append(pgm)
        groups[pgm][0].append(xi)
        groups[pgm][1].append(yi)
    return [(groups[p][0], groups[p][1], p) for p in order]


def create_1rm_plots(datatype: str, x: list, y: list, exercise: str) -> None:
    """Plot training data 1RM with fit.

    :param datatype: Data type: real or simulated
    :type datatype: str
    :param x: x-axis data (Unix timestamps)
    :type x: list
    :param y: y-axis data (1RM estimates in kg)
    :type y: list
    :param exercise: Exercise name
    :type exercise: str
    """

    plt.figure(figsize=(8, 8))

    if len(x) < 5:
        sns.set_theme()
        ax = sns.scatterplot(x=x, y=y)
        ax.set_title(f"{exercise}")
    else:
        groups = _split_by_program(x, y)
        ax = None
        for i, (xg, yg, pgm_name) in enumerate(groups):
            if len(xg) < 2:
                continue
            truncate = i > 0
            plot = sns.regplot(x=xg, y=yg, ci=68, truncate=truncate, label=pgm_name)
            if ax is None:
                ax = plot
        if ax is None:
            ax = sns.scatterplot(x=x, y=y)
        ax.set_title(f"{exercise}", fontsize=30)

    xticks = ax.get_xticks()
    xticks_dates = [datetime.fromtimestamp(t).strftime("%Y-%m-%d") for t in xticks]
    ax.set_xticklabels(xticks_dates)
    plt.ylim(0, max(y) + 5)
    plt.xticks(rotation=45)
    ax.set_ylabel("1 RM estimates [kg]", fontsize=20)
    ax.legend(loc="lower right", fontsize=20)

    plt.savefig(
        f"{settings['IMG_PATH']}all_years/one_rep_max/{datatype}_fitted_data_{exercise}_splines.png"
    )
    plt.clf()


def create_volume_plots(datatype: str, x: list, y: list, exercise: str) -> None:
    """Create volume plots.

    :param datatype: Data type: real or simulated
    :type datatype: str
    :param x: x-axis data (Unix timestamps)
    :type x: list
    :param y: y-axis data (volume in kg)
    :type y: list
    :param exercise: Exercise name
    :type exercise: str
    """

    plt.figure(figsize=(8, 8))

    groups = _split_by_program(x, y)
    ax = None
    for xg, yg, pgm_name in groups:
        if len(xg) < 2:
            continue
        plot = sns.regplot(x=xg, y=yg, ci=68, label=pgm_name)
        if ax is None:
            ax = plot

    if ax is None:
        ax = sns.scatterplot(x=x, y=y)

    ax.set_title(f"{exercise}", fontsize=30)
    xticks = ax.get_xticks()
    xticks_dates = [datetime.fromtimestamp(t).strftime("%Y-%m-%d") for t in xticks]
    ax.set_xticklabels(xticks_dates)
    plt.ylim(0, max(y) + 5)
    plt.xticks(rotation=45)
    ax.set_ylabel("Volume [kg]", fontsize=20)
    ax.legend(loc="lower right", fontsize=20)
    plt.savefig(
        f"{settings['IMG_PATH']}all_years/volume/{datatype}_fitted_data_{exercise}_gvt.png"
    )
    plt.clf()


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
