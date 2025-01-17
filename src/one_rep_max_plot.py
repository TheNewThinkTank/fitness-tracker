"""
Plots of popular 1-repetition-maximum formulas.
"""

# import os
# import sys
# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.dirname(SCRIPT_DIR))
import matplotlib.pyplot as plt  # type: ignore
import numpy as np  # type: ignore
import pandas as pd  # type: ignore
import seaborn as sns  # type: ignore
from src.one_rep_max import EpleyStrategy, BrzyckiStrategy  # type: ignore
from src.one_rep_max_calc import (  # type: ignore
    OneRepMaxCalculator,
    EpleyInvertedStrategy,
    BrzyckiInvertedStrategy,
    InvertedCalculator
    )


def get_data() -> tuple:
    """Get data for plotting 1-repetition-maximum formulas.

    :return: tuple of dataframes
    :rtype: tuple
    """

    epley_calculator = OneRepMaxCalculator(EpleyStrategy())
    brzycki_calculator = OneRepMaxCalculator(BrzyckiStrategy())
    epley_inverted_calculator = InvertedCalculator(EpleyInvertedStrategy())
    brzycki_inverted_calculator = InvertedCalculator(BrzyckiInvertedStrategy())

    weight = np.array(range(10, 60, 10))
    reps = np.array(range(2, 10))
    constant_weight = np.full(reps.size, 70)
    constant_reps = np.full(weight.size, 5)

    # evaluate 1rm formulas at 5 reps for varying weights
    one_rm_constant_reps_df = pd.DataFrame(
        {
            "weight": weight,
            "epley_1rm": epley_calculator.calculate(weight, constant_reps),
            "brzycki_1rm": brzycki_calculator.calculate(weight, constant_reps)
        }
    )
    df1 = one_rm_constant_reps_df[['weight', 'epley_1rm', 'brzycki_1rm']]
    df1 = df1.melt(id_vars='weight', var_name='variable', value_name='one_rep_max')

    # evaluate 1rm formulas at weight: 70 kg for varying reps
    one_rm_constant_weight_df = pd.DataFrame(
        {
            "reps": reps,
            "epley_1rm": epley_calculator.calculate(constant_weight, reps),
            "brzycki_1rm": brzycki_calculator.calculate(constant_weight, reps)
        }
    )
    df2 = one_rm_constant_weight_df[['reps', 'epley_1rm', 'brzycki_1rm']]
    df2 = df2.melt(id_vars='reps', var_name='variable', value_name='one_rep_max')

    # evaluate inverse 1rm formulas at 5 reps for varying weights
    inverse_one_rm_constant_reps_df = pd.DataFrame(
        {
            "weight": weight,
            "epley_inverted": epley_inverted_calculator.calculate(weight, constant_reps, 10),
            "brzycki_inverted": brzycki_inverted_calculator.calculate(weight, constant_reps, 10)
        }
    )
    df3 = inverse_one_rm_constant_reps_df[['weight', 'epley_inverted', 'brzycki_inverted']]
    df3 = df3.melt(id_vars='weight', var_name='variable', value_name='inverse_one_rep_max')

    # evaluate inverse 1rm formulas at weight: 70 kg for varying reps
    inverse_one_rm_constant_weight_df = pd.DataFrame(
        {
            "reps": reps,
            "epley_inverted": epley_inverted_calculator.calculate(constant_weight, reps, 10),
            "brzycki_inverted": brzycki_inverted_calculator.calculate(constant_weight, reps, 10)
        }
    )
    df4 = inverse_one_rm_constant_weight_df[['reps', 'epley_inverted', 'brzycki_inverted']]
    df4 = df4.melt(id_vars='reps', var_name='variable', value_name='inverse_one_rep_max')

    return df1, df2, df3, df4


def make_plots(
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        df3: pd.DataFrame,
        df4: pd.DataFrame
        ) -> None:
    """Make plots of 1-repetition-maximum formulas.

    :param df1: dataframe with weight, one_rep_max, and variable columns
    :type df1: pd.DataFrame
    :param df2: dataframe with reps, one_rep_max, and variable columns
    :type df2: pd.DataFrame
    :param df3: dataframe with weight, inverse_one_rep_max, and variable columns
    :type df3: pd.DataFrame
    :param df4: dataframe with reps, inverse_one_rep_max, and variable columns
    :type df4: pd.DataFrame
    """
    _, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 8))

    # Plot 1
    if not isinstance(axes, np.ndarray):
        axes = np.array([axes])

    hue = 'variable'
    palette = ['darkred', 'steelblue']
    legend_title = 'Variable'

    sns.scatterplot(
        data=df1,
        x='weight',
        y='one_rep_max',
        hue=hue,
        palette=palette,
        ax=axes[0, 0]
        )
    axes[0, 0].set_title('Constant reps (5)')
    axes[0, 0].set_xlabel('Weight')
    axes[0, 0].set_ylabel('One Rep Max')
    axes[0, 0].legend(title=legend_title)

    # Plot 2
    sns.scatterplot(
        data=df2,
        x='reps',
        y='one_rep_max',
        hue=hue,
        palette=palette,
        ax=axes[0, 1]
        )
    axes[0, 1].set_title('Constant weight (70 kg)')
    axes[0, 1].set_xlabel('Reps')
    axes[0, 1].set_ylabel('One Rep Max')
    axes[0, 1].legend(title=legend_title)

    # Plot 3
    sns.scatterplot(
        data=df3,
        x='weight',
        y='inverse_one_rep_max',
        hue=hue,
        palette=palette,
        ax=axes[1, 0]
        )
    axes[1, 0].set_title('Constant reps (5)')
    axes[1, 0].set_xlabel('Weight')
    axes[1, 0].set_ylabel('Inverse One Rep Max')
    axes[1, 0].legend(title=legend_title)

    # Plot 4
    sns.scatterplot(
        data=df4,
        x='reps',
        y='inverse_one_rep_max',
        hue=hue,
        palette=palette,
        ax=axes[1, 1]
        )
    axes[1, 1].set_title('Constant weight (70 kg)')
    axes[1, 1].set_xlabel('Reps')
    axes[1, 1].set_ylabel('Inverse One Rep Max')
    axes[1, 1].legend(title=legend_title)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    make_plots(*get_data())
