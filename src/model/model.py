"""
read workout data and calculate 1RM and training volume.
"""

from datetime import datetime
import logging
import os
import sys
from typing import Final
import pandas as pd  # type: ignore
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from utils.set_db_and_table import set_db_and_table  # type: ignore
from one_rep_max import (  # type: ignore
    ACSMStrategy,
    EpleyStrategy,
    BrzyckiStrategy
    )
from one_rep_max_calc import OneRepMaxCalculator  # type: ignore


def get_df(
    log,
    splits: list[str] = ["chest", "push", "chest_and_back"],
    exercise: str = "barbell_bench_press",
) -> pd.DataFrame:
    """Return one consolidated Pandas dataframe,
    containing workout date and training data,
    for specified split(s) and exercise.

    :param log: _description_
    :type log: _type_
    :param splits: _description_, defaults to ["chest", "push", "chest_and_back"]
    :type splits: list, optional
    :param exercise: _description_, defaults to "barbell_bench_press"
    :type exercise: str, optional
    :return: _description_
    :rtype: pd.DataFrame
    """

    frames = []
    for item in log:
        if any(x in item["split"] for x in splits):
            if exercise in item["exercises"].keys():
                df = pd.DataFrame(item["exercises"][exercise])
                df["date"] = item["date"]
                frames.append(df)

    return pd.concat(frames)


def get_weight(df: pd.DataFrame) -> pd.Series:
    """_summary_

    :param df: _description_
    :type df: pd.DataFrame
    :return: _description_
    :rtype: pd.DataFrame
    """

    return df["weight"].str.strip(" kg").astype(float)


def calc_volume(df: pd.DataFrame) -> pd.DataFrame:
    """sets times reps times load.

    :param df: _description_
    :type df: pd.DataFrame
    :return: _description_
    :rtype: pd.DataFrame
    """

    df_copy = df.copy()
    num_of_sets_df = df_copy.groupby("date")[["set_number"]].agg("max")
    reps_df = df_copy.groupby("date")[["reps"]].agg("max")
    df_copy["weight"] = get_weight(df_copy)
    weight_df = df_copy.groupby("date")[["weight"]].agg("max")
    df_res = pd.concat([num_of_sets_df, reps_df, weight_df], axis=1)
    df_res["volume"] = df_res["set_number"] * df_res["reps"] * df_res["weight"]

    return df_res.drop(["set_number", "reps", "weight"], axis=1)


def one_rep_max_estimator(df: pd.DataFrame, formula="acsm") -> pd.DataFrame:
    """Estimates 1RM using ACSM, Epley, or Brzycki formulas.

    :param df: DataFrame containing weight and reps data
    :type df: pd.DataFrame
    :param formula: Formula to use ('acsm', 'epley', or 'brzycki'), defaults to "acsm"
    :type formula: str, optional
    :return: DataFrame with estimated 1RM per date
    :rtype: pd.DataFrame
    """
    df_copy = df.copy()

    # Define strategies based on the input formula
    match formula.lower():
        case "acsm":
            strategy = ACSMStrategy()
        case "epley":
            strategy = EpleyStrategy()
        case "brzycki":
            strategy = BrzyckiStrategy()
        case _:
            sys.exit("Invalid formula. Use 'acsm', 'epley', or 'brzycki'.")

    # Initialize calculator with the selected strategy
    calculator = OneRepMaxCalculator(strategy)

    # Vectorized calculation for the whole DataFrame
    weights = get_weight(df_copy)
    reps = df_copy['reps']  # .astype(int)

    df_copy["1RM"] = calculator.calculate(weights, reps)

    # Return the max 1RM per date
    return df_copy.groupby("date")[["1RM"]].agg("max")


def get_data(df, y_col="1RM") -> tuple[list[float], list[float]]:
    """Get workout-timestamps and 1RM estimates.

    :param df: Pandas dataframe with workout-timestamps
        and either 1RM estimates or volume
    :type df: pd.DataFrame
    :param y_col: String signifying whether to use 1RM estimates or volume
    :type y_col: str
    :return: workout-timestamps and either 1RM estimates or volume
    :rtype: tuple[list[float], list[float]]
    """

    date_strs = df.index.tolist()  # workout-dates
    x = [datetime.fromisoformat(i).timestamp() for i in date_strs]

    match y_col:
        case "1RM":
            y = df["1RM"].tolist()  # max 1RM estimate in kg
            y = [float("{:.2f}".format(x)) for x in y]
        case "volume":
            y = df["volume"].tolist()  # volume in kg
        case _:
            raise ValueError

    return x, y


def main() -> None:
    """Prepare dfs, calc 1RM and do linear regression."""

    from utils.logger_config import setup_logger, log_running_file  # type: ignore

    setup_logger(log_file="model.log")
    log_running_file(__file__)

    logger1 = logging.getLogger("model.area1")
    logger2 = logging.getLogger("model.area2")

    DATA_MODELS = ["real", "simulated"]
    FORMULAS = ["acsm", "epley", "brzycki"]
    datatype = DATA_MODELS[0]
    _EXERCISE: Final[str] = "squat"
    _SPLITS: Final[list[str]] = ["legs", "legs_and_abs"]
    db, table, _ = set_db_and_table(datatype)

    logger1.info("data_model: %s", datatype)
    logger1.debug("db: %s", db)
    logger1.debug("table: %s", table)

    workout_timestamps, one_rm_estimates = get_data(
        one_rep_max_estimator(
            get_df(table, splits=_SPLITS, exercise=_EXERCISE),
            formula=FORMULAS[0],
        )
    )

    workout_timestamps, volume = get_data(
        calc_volume(get_df(table, splits=_SPLITS, exercise=_EXERCISE)),
        y_col="volume",
    )

    logger2.info("Exercise: %s", _EXERCISE)
    logger2.info("Workout timestamps: %s", workout_timestamps)
    logger2.info("1 RM estimates: %s", one_rm_estimates)
    logger2.info("Volume: %s", volume)


if __name__ == "__main__":
    main()
