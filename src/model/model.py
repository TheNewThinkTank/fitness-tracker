"""
Read workout data and calculate 1RM and training volume.
"""

from datetime import datetime
import re
import sys
from typing import Final
import pandas as pd  # type: ignore
from loguru import logger  # type: ignore
from src.utils.set_db_and_table import set_db_and_table  # type: ignore
from src.one_rep_max import (  # type: ignore
    OneRepMaxStrategy,
    ACSMStrategy,
    EpleyStrategy,
    BrzyckiStrategy
    )
from src.one_rep_max_calc import OneRepMaxCalculator  # type: ignore


def get_df(
    table,
    splits: list[str] = ["chest", "push", "chest_and_back"],
    exercise: str = "barbell_bench_press",
) -> pd.DataFrame:
    """Return one consolidated Pandas dataframe,
    containing workout date and training data,
    for specified split(s) and exercise.

    :param table: TinyDB table
    :type table: tinydb.table.Table
    :param splits: List of workout splits to include,
      defaults to ["chest", "push", "chest_and_back"]
    :type splits: list, optional
    :param exercise: Exercise to include, defaults to "barbell_bench_press"
    :type exercise: str, optional
    :return: Consolidated Pandas dataframe
    :rtype: pd.DataFrame
    """

    frames = []
    for item in table:
        if not any(x in item["split"] for x in splits):
            continue
        if exercise in item["exercises"].keys():
            df = pd.DataFrame(item["exercises"][exercise])
            df["date"] = item["date"]
            frames.append(df)

    return pd.concat(frames)


def get_weight(df: pd.DataFrame) -> pd.Series:
    """Extracts numeric weight in kg from the 'weight' column.

    Handles plain weights ("80 kg"), bodyweight-only ("BODYWEIGHT" → 0),
    and bodyweight-offset forms ("BODYWEIGHT + 10 kg" → 10, "BODYWEIGHT - 5 kg" → -5).

    :param df: Pandas dataframe with 'weight' column
    :type df: pd.DataFrame
    :return: Weight in kg as float
    :rtype: pd.Series
    """

    def _parse(value: str) -> float:
        value = value.strip()
        if value == "BODYWEIGHT":
            return 0.0
        m = re.match(
            r"^BODYWEIGHT\s*([+-])\s*(\d+(?:\.\d+)?)\s*kg$", value, re.IGNORECASE
        )
        if m:
            sign = 1 if m.group(1) == "+" else -1
            return sign * float(m.group(2))
        m = re.match(r"^(\d+(?:\.\d+)?)\s*kg$", value)
        if m:
            return float(m.group(1))
        raise ValueError(f"Cannot parse weight: {value!r}")

    return df["weight"].map(_parse)


def calc_volume(df: pd.DataFrame) -> pd.DataFrame:
    """Sets times reps times load.

    :param df: DataFrame containing weight, reps, and set_number data
    :type df: pd.DataFrame
    :return: DataFrame with volume per date
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


def one_rep_max_estimator(df: pd.DataFrame, formula: str="acsm") -> pd.DataFrame:
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
    strategy: OneRepMaxStrategy
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

    from src.utils.logger_config import setup_logger, log_running_file  # type: ignore

    setup_logger(log_file="model.log")
    log_running_file(__file__)

    DATA_MODELS = ["real", "simulated"]
    FORMULAS = ["acsm", "epley", "brzycki"]
    datatype = DATA_MODELS[0]
    _EXERCISE: Final[str] = "squat"
    _SPLITS: Final[list[str]] = ["legs", "legs_and_abs"]
    db, table, _ = set_db_and_table(datatype)

    logger.info("data_model: {}", datatype)
    logger.debug("db: {}", db)
    logger.debug("table: {}", table)

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

    logger.info("Exercise: {}", _EXERCISE)
    logger.info("Workout timestamps: {}", workout_timestamps)
    logger.info("1 RM estimates: {}", one_rm_estimates)
    logger.info("Volume: {}", volume)


if __name__ == "__main__":
    main()
